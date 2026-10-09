package server

import (
	"encoding/json"
	"net/http/httptest"
	"testing"
)

func TestHealthHandler(t *testing.T) {
	router := InitRouter()
	req := httptest.NewRequest("GET", "/health", nil)
	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 200 { t.Errorf("expected 200, got %d", rr.Code) }
}

func TestLoadModuleAuthFailures(t *testing.T) {
	router := InitRouter()
	
	// Test without auth token
	t.Setenv("MODULE_API_TOKEN", "testtoken")
	req := httptest.NewRequest("POST", "/module/load/testmod", nil)
	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 401 { t.Errorf("expected 401, got %d", rr.Code) }

	// Test with wrong token
	req = httptest.NewRequest("POST", "/module/load/testmod", nil)
	req.Header.Set("Authorization", "Bearer wrongtoken")
	rr = httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 401 { t.Errorf("expected 401, got %d", rr.Code) }

	// Test without env token
	t.Setenv("MODULE_API_TOKEN", "")
	req = httptest.NewRequest("POST", "/module/load/testmod", nil)
	rr = httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 503 { t.Errorf("expected 503, got %d", rr.Code) }
}

func TestDiagnoseHandler(t *testing.T) {
	router := InitRouter()
	t.Setenv("MODULE_API_TOKEN", "testtoken")

	// Test without auth
	req := httptest.NewRequest("POST", "/module/testmod/diagnose", nil)
	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 401 { t.Errorf("expected 401, got %d", rr.Code) }

	// Test with invalid module name
	req = httptest.NewRequest("POST", "/module/invalid_mod!/diagnose", nil)
	req.Header.Set("Authorization", "Bearer testtoken")
	rr = httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 400 { t.Errorf("expected 400, got %d", rr.Code) }

	// Test diagnose endpoint without AI_SERVICE_URL
	t.Setenv("AI_SERVICE_URL", "")
	req = httptest.NewRequest("POST", "/module/testmod/diagnose", nil)
	req.Header.Set("Authorization", "Bearer testtoken")
	rr = httptest.NewRecorder()
	router.ServeHTTP(rr, req)
	if rr.Code != 200 { t.Errorf("expected 200, got %d", rr.Code) }
	
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
