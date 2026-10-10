package server

import (
	"encoding/json"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestHealthHandler(t *testing.T) {
	router := InitRouter()
	req := httptest.NewRequest("GET", "/health", nil)
	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 200 {
		t.Errorf("expected 200, got %d", rr.Code)
	}
}

func TestLoadModuleAuthFailures(t *testing.T) {
	router := InitRouter()

	// Test without auth token
	t.Setenv("MODULE_API_TOKEN", "testtoken")
	req := httptest.NewRequest("POST", "/module/load/nvidia", nil)
	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 401 {
		t.Errorf("expected 401, got %d", rr.Code)
	}

	// Test with wrong token
	req = httptest.NewRequest("POST", "/module/load/nvidia", nil)
	req.Header.Set("Authorization", "Bearer wrongtoken")
	rr = httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 401 {
		t.Errorf("expected 401, got %d", rr.Code)
	}

	// Test without env token configured
	t.Setenv("MODULE_API_TOKEN", "")
	t.Setenv("READONLY_API_TOKEN", "")
	req = httptest.NewRequest("POST", "/module/load/nvidia", nil)
	rr = httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 503 {
		t.Errorf("expected 503, got %d", rr.Code)
	}
}

func TestDryRunExecution(t *testing.T) {
	router := InitRouter()
	t.Setenv("MODULE_API_TOKEN", "testadmin")

	// Dry run load
	req := httptest.NewRequest("POST", "/module/load/nvidia?dry_run=true", nil)
	req.Header.Set("Authorization", "Bearer testadmin")
	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 200 {
		t.Errorf("expected 200 for dry run, got %d", rr.Code)
	}
	var resp map[string]any
	_ = json.NewDecoder(rr.Body).Decode(&resp)
	if resp["dry_run"] != true {
		t.Errorf("expected dry_run=true in response, got %v", resp["dry_run"])
	}
}

func TestCriticalDenylistProtection(t *testing.T) {
	router := InitRouter()
	t.Setenv("MODULE_API_TOKEN", "testadmin")

	// Attempt to unload ext4 filesystem driver
	req := httptest.NewRequest("POST", "/module/unload/ext4", nil)
	req.Header.Set("Authorization", "Bearer testadmin")
	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 400 {
		t.Errorf("expected 400 for protected module unload, got %d", rr.Code)
	}
	if !strings.Contains(rr.Body.String(), "critical system denylist") {
		t.Errorf("expected critical denylist message, got %s", rr.Body.String())
	}
}

func TestReadOnlyTokenScope(t *testing.T) {
	router := InitRouter()
	t.Setenv("MODULE_API_TOKEN", "admin_secret")
	t.Setenv("READONLY_API_TOKEN", "readonly_secret")

	// Readonly token attempting privileged load must be rejected
	req := httptest.NewRequest("POST", "/module/load/nvidia", nil)
	req.Header.Set("Authorization", "Bearer readonly_secret")
	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 401 {
		t.Errorf("expected 401 for privileged action with read token, got %d", rr.Code)
	}

	// Readonly token allowed on diagnose
	t.Setenv("AI_SERVICE_URL", "")
	req = httptest.NewRequest("POST", "/module/nvidia/diagnose", nil)
	req.Header.Set("Authorization", "Bearer readonly_secret")
	rr = httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 200 {
		t.Errorf("expected 200 for diagnose with read token, got %d", rr.Code)
	}
}

func TestDiagnoseHandler(t *testing.T) {
	router := InitRouter()
	t.Setenv("MODULE_API_TOKEN", "testtoken")

	// Test without auth
	req := httptest.NewRequest("POST", "/module/testmod/diagnose", nil)
	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 401 {
		t.Errorf("expected 401, got %d", rr.Code)
	}

	// Test with invalid module name
	req = httptest.NewRequest("POST", "/module/invalid_mod!/diagnose", nil)
	req.Header.Set("Authorization", "Bearer testtoken")
	rr = httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 400 {
		t.Errorf("expected 400, got %d", rr.Code)
	}

	// Test diagnose endpoint without AI_SERVICE_URL
	t.Setenv("AI_SERVICE_URL", "")
	req = httptest.NewRequest("POST", "/module/testmod/diagnose", nil)
	req.Header.Set("Authorization", "Bearer testtoken")
	rr = httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 200 {
		t.Errorf("expected 200, got %d", rr.Code)
	}

	var resp map[string]interface{}
	if err := json.NewDecoder(rr.Body).Decode(&resp); err != nil {
		t.Errorf("invalid json: %v", err)
	}
	if resp["note"] != "AI_SERVICE_URL not configured" {
		t.Errorf("expected note 'AI_SERVICE_URL not configured', got %v", resp["note"])
	}
	if _, ok := resp["evidence"]; !ok {
		t.Errorf("expected evidence in response")
	}
}
