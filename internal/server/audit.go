package server

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"sync"
	"time"
)

// AuditEntry records a security-relevant event.
type AuditEntry struct {
	Timestamp time.Time `json:"timestamp"`
	RequestID string    `json:"request_id"`
	CallerID  string    `json:"caller_id"` // Salted hash prefix of token, never the raw token
	Action    string    `json:"action"`    // load, unload, diagnose
	Module    string    `json:"module"`
	Result    string    `json:"result"` // success, denied, error
	Message   string    `json:"message,omitempty"`
}

var (
	auditMu  sync.Mutex
	auditLog *os.File
)

// MaskToken produces an anonymous identifier (first 12 chars of SHA256) for audit logs.
func MaskToken(token string) string {
	if token == "" {
		return "anonymous"
	}
	h := sha256.Sum256([]byte(token))
	return hex.EncodeToString(h[:])[:12]
}

// LogAudit writes an append-only JSON audit record.
func LogAudit(entry AuditEntry) {
	auditMu.Lock()
	defer auditMu.Unlock()

	entry.Timestamp = time.Now().UTC()
	bytes, err := json.Marshal(entry)
	if err != nil {
		return
	}

	// Write to stderr / stdout
	fmt.Fprintf(os.Stderr, "[AUDIT] %s\n", string(bytes))

	// If AUDIT_LOG_FILE is specified, write to disk
	auditPath := os.Getenv("AUDIT_LOG_FILE")
	if auditPath != "" {
		if auditLog == nil {
			f, err := os.OpenFile(auditPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600)
			if err == nil {
				auditLog = f
			}
		}
		if auditLog != nil {
			_, _ = auditLog.Write(append(bytes, '\n'))
		}
	}
}
