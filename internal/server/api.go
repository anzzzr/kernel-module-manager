package server

import (
	"bytes"
	"crypto/subtle"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/anzzzr/kernel-module-manager/modules"
	"github.com/gorilla/mux"
)

// RateLimiter tracks per-token request frequency.
type RateLimiter struct {
	mu       sync.Mutex
	requests map[string][]time.Time
	limit    int           // requests
	window   time.Duration // window
}

var globalLimiter = &RateLimiter{
	requests: make(map[string][]time.Time),
	limit:    30, // 30 requests per minute per token
	window:   time.Minute,
}

func (rl *RateLimiter) Allow(tokenID string) bool {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	now := time.Now()
	cutoff := now.Add(-rl.window)

	valid := []time.Time{}
	for _, t := range rl.requests[tokenID] {
		if t.After(cutoff) {
			valid = append(valid, t)
		}
	}

	if len(valid) >= rl.limit {
		return false
	}
	rl.requests[tokenID] = append(valid, now)
	return true
}

func writeJSON(w http.ResponseWriter, code int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(v)
}

// Constant-time token verification supporting separate privileged and read-only tokens.
// Scope: "admin" (load/unload) vs "read" (diagnose).
func authorizeScoped(w http.ResponseWriter, r *http.Request, scope string) (bool, string) {
	adminToken := os.Getenv("MODULE_API_TOKEN")
	readToken := os.Getenv("READONLY_API_TOKEN")

	if adminToken == "" && readToken == "" {
		writeJSON(w, http.StatusServiceUnavailable, map[string]string{"error": "MODULE_API_TOKEN must be configured"})
		return false, ""
	}

	authHeader := r.Header.Get("Authorization")
	if !strings.HasPrefix(authHeader, "Bearer ") {
		writeJSON(w, http.StatusUnauthorized, map[string]string{"error": "unauthorized"})
		return false, ""
	}
	providedToken := strings.TrimPrefix(authHeader, "Bearer ")
	callerID := MaskToken(providedToken)

	// Rate limiting check
	if !globalLimiter.Allow(callerID) {
		writeJSON(w, http.StatusTooManyRequests, map[string]string{"error": "rate limit exceeded"})
		return false, callerID
	}

	isAdmin := adminToken != "" && subtle.ConstantTimeCompare([]byte(providedToken), []byte(adminToken)) == 1
	isReader := readToken != "" && subtle.ConstantTimeCompare([]byte(providedToken), []byte(readToken)) == 1

	if scope == "admin" {
		if !isAdmin {
			writeJSON(w, http.StatusUnauthorized, map[string]string{"error": "privileged token required"})
			return false, callerID
		}
		return true, callerID
	}

	// Read scope: permitted by either admin token or readonly token
	if isAdmin || isReader {
		return true, callerID
	}

	writeJSON(w, http.StatusUnauthorized, map[string]string{"error": "unauthorized"})
	return false, callerID
}

func loadModuleHandler(w http.ResponseWriter, r *http.Request) {
	reqID := fmt.Sprintf("req-%d", time.Now().UnixNano())
	authorized, callerID := authorizeScoped(w, r, "admin")
	if !authorized {
		LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "load", Result: "unauthorized"})
		return
	}

	name := mux.Vars(r)["module"]
	policy := modules.GetPolicy()
	allowed, reason := policy.CanLoad(name)
	if !allowed {
		LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "load", Module: name, Result: "denied", Message: reason})
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": reason})
		return
	}

	// Check dry-run parameter
	dryRun := r.URL.Query().Get("dry_run") == "true"
	if dryRun {
		LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "load_dry_run", Module: name, Result: "success"})
		writeJSON(w, http.StatusOK, map[string]any{
			"dry_run": true,
			"command": fmt.Sprintf("modprobe %s", name),
			"message": fmt.Sprintf("Dry-run: module %s would be loaded", name),
		})
		return
	}

	if err := modules.LoadModule(name); err != nil {
		LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "load", Module: name, Result: "error", Message: err.Error()})
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": err.Error()})
		return
	}

	LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "load", Module: name, Result: "success"})
	writeJSON(w, http.StatusOK, map[string]string{"message": fmt.Sprintf("Module %s loaded", name)})
}

func unloadModuleHandler(w http.ResponseWriter, r *http.Request) {
	reqID := fmt.Sprintf("req-%d", time.Now().UnixNano())
	authorized, callerID := authorizeScoped(w, r, "admin")
	if !authorized {
		LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "unload", Result: "unauthorized"})
		return
	}

	name := mux.Vars(r)["module"]
	policy := modules.GetPolicy()
	allowed, reason := policy.CanUnload(name)
	if !allowed {
		LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "unload", Module: name, Result: "denied", Message: reason})
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": reason})
		return
	}

	// Safety check: Prevent unloading modules with active refcounts
	inUse, refCount, usedBy, _ := modules.IsModuleInUse(name)
	if inUse {
		msg := fmt.Sprintf("module %s is currently in use (refcount=%d, used_by=%v)", name, refCount, usedBy)
		LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "unload", Module: name, Result: "denied", Message: msg})
		writeJSON(w, http.StatusConflict, map[string]any{
			"error":    msg,
			"refcount": refCount,
			"used_by":  usedBy,
		})
		return
	}

	// Check dry-run parameter
	dryRun := r.URL.Query().Get("dry_run") == "true"
	if dryRun {
		LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "unload_dry_run", Module: name, Result: "success"})
		writeJSON(w, http.StatusOK, map[string]any{
			"dry_run": true,
			"command": fmt.Sprintf("rmmod %s", name),
			"message": fmt.Sprintf("Dry-run: module %s would be unloaded", name),
		})
		return
	}

	if err := modules.UnloadModule(name); err != nil {
		LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "unload", Module: name, Result: "error", Message: err.Error()})
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": err.Error()})
		return
	}

	LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "unload", Module: name, Result: "success"})
	writeJSON(w, http.StatusOK, map[string]string{"message": fmt.Sprintf("Module %s unloaded", name)})
}

func diagnoseHandler(w http.ResponseWriter, r *http.Request) {
	reqID := fmt.Sprintf("req-%d", time.Now().UnixNano())
	authorized, callerID := authorizeScoped(w, r, "read")
	if !authorized {
		LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "diagnose", Result: "unauthorized"})
		return
	}

	name := mux.Vars(r)["module"]
	if !modules.ValidModule(name) {
		LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "diagnose", Module: name, Result: "denied", Message: "invalid module format"})
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid module name"})
		return
	}

	atomic.AddUint64(&stats.DiagnoseRequests, 1)
	tCollectStart := time.Now()
	evidence := modules.Diagnose(name)
	collectDuration := float64(time.Since(tCollectStart).Microseconds()) / 1000.0
	recordLatency(collectDuration)

	payload, _ := json.Marshal(evidence)
	url := strings.TrimRight(os.Getenv("AI_SERVICE_URL"), "/")
	if url == "" {
		LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "diagnose", Module: name, Result: "success_local"})
		writeJSON(w, http.StatusOK, map[string]any{
			"evidence":   evidence,
			"note":       "AI_SERVICE_URL not configured",
			"request_id": reqID,
			"collect_ms": collectDuration,
		})
		return
	}

	client := &http.Client{Timeout: 35 * time.Second}
	req, err := http.NewRequestWithContext(r.Context(), "POST", url+"/analyze", bytes.NewReader(payload))
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": err.Error(), "request_id": reqID})
		return
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Request-ID", reqID)
	if key := os.Getenv("AI_SERVICE_TOKEN"); key != "" {
		req.Header.Set("Authorization", "Bearer "+key)
	}

	resp, err := client.Do(req)
	if err != nil {
		atomic.AddUint64(&stats.ErrorCount, 1)
		LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "diagnose", Module: name, Result: "ai_unavailable"})
		// Graceful degraded response returning raw evidence summary instead of hard 500
		writeJSON(w, http.StatusOK, map[string]any{
			"module":     name,
			"evidence":   evidence,
			"ai_status":  "unavailable",
			"error":      "AI service temporarily unreachable: " + err.Error(),
			"request_id": reqID,
			"collect_ms": collectDuration,
		})
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(io.LimitReader(resp.Body, 100000))
	if err != nil {
		atomic.AddUint64(&stats.ErrorCount, 1)
		writeJSON(w, http.StatusBadGateway, map[string]string{"error": "invalid AI response", "request_id": reqID})
		return
	}

	atomic.AddUint64(&stats.SuccessfulActions, 1)
	LogAudit(AuditEntry{RequestID: reqID, CallerID: callerID, Action: "diagnose", Module: name, Result: "success"})
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("X-Request-ID", reqID)
	w.WriteHeader(resp.StatusCode)
	_, _ = w.Write(body)
}

// InitRouter registers HTTP endpoints.
func InitRouter() *mux.Router {
	router := mux.NewRouter()
	router.HandleFunc("/module/load/{module}", loadModuleHandler).Methods("POST")
	router.HandleFunc("/module/unload/{module}", unloadModuleHandler).Methods("POST")
	router.HandleFunc("/module/{module}/diagnose", diagnoseHandler).Methods("POST")
	router.HandleFunc("/stats", statsHandler).Methods("GET")
	router.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
	}).Methods("GET")
	return router
}
