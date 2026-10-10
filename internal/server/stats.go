package server

import (
	"encoding/json"
	"net/http"
	"sync"
	"sync/atomic"
	"time"
)

// ServerMetrics holds thread-safe operational statistics for the Go daemon.
type ServerMetrics struct {
	TotalRequests     uint64 `json:"total_requests"`
	DiagnoseRequests  uint64 `json:"diagnose_requests"`
	LoadRequests      uint64 `json:"load_requests"`
	UnloadRequests    uint64 `json:"unload_requests"`
	AuthFailures      uint64 `json:"auth_failures"`
	DeniedRequests    uint64 `json:"denied_requests"`
	RateLimitHits     uint64 `json:"rate_limit_hits"`
	SuccessfulActions uint64 `json:"successful_actions"`
	ErrorCount        uint64 `json:"error_count"`

	mu             sync.Mutex
	collectLatency []float64 // ms
}

var stats = &ServerMetrics{}

func recordLatency(ms float64) {
	stats.mu.Lock()
	defer stats.mu.Unlock()
	stats.collectLatency = append(stats.collectLatency, ms)
	if len(stats.collectLatency) > 500 {
		stats.collectLatency = stats.collectLatency[1:]
	}
}

func getAvgLatency() float64 {
	stats.mu.Lock()
	defer stats.mu.Unlock()
	if len(stats.collectLatency) == 0 {
		return 0.0
	}
	var sum float64
	for _, l := range stats.collectLatency {
		sum += l
	}
	return sum / float64(len(stats.collectLatency))
}

func statsHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)

	payload := map[string]any{
		"service":            "kernel-module-manager-go",
		"timestamp":          time.Now().UTC(),
		"total_requests":     atomic.LoadUint64(&stats.TotalRequests),
		"diagnose_requests":  atomic.LoadUint64(&stats.DiagnoseRequests),
		"load_requests":      atomic.LoadUint64(&stats.LoadRequests),
		"unload_requests":    atomic.LoadUint64(&stats.UnloadRequests),
		"auth_failures":      atomic.LoadUint64(&stats.AuthFailures),
		"denied_requests":    atomic.LoadUint64(&stats.DeniedRequests),
		"rate_limit_hits":    atomic.LoadUint64(&stats.RateLimitHits),
		"successful_actions": atomic.LoadUint64(&stats.SuccessfulActions),
		"error_count":        atomic.LoadUint64(&stats.ErrorCount),
		"avg_collect_ms":     getAvgLatency(),
	}
	_ = json.NewEncoder(w).Encode(payload)
}
