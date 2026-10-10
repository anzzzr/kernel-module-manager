package modules

import (
	"strings"
	"testing"
)

func TestRedactIPv4(t *testing.T) {
	input := "Connected from 192.168.1.50 to external 10.0.0.1 via interface"
	redacted := RedactEvidence(input)
	if strings.Contains(redacted, "192.168.1.50") || strings.Contains(redacted, "10.0.0.1") {
		t.Errorf("failed to redact IP address: %s", redacted)
	}
	if !strings.Contains(redacted, "[REDACTED_IP]") {
		t.Errorf("expected [REDACTED_IP] in output: %s", redacted)
	}
	// Verify localhost 127.0.0.1 is preserved for local IPC references
	local := "Service running on 127.0.0.1:8001"
	if RedactEvidence(local) != local {
		t.Errorf("expected 127.0.0.1 to be preserved: %s", RedactEvidence(local))
	}
}

func TestRedactMAC(t *testing.T) {
	input := "eth0: link up, MAC address 00:15:5d:01:02:03"
	redacted := RedactEvidence(input)
	if strings.Contains(redacted, "00:15:5d:01:02:03") {
		t.Errorf("failed to redact MAC: %s", redacted)
	}
	if !strings.Contains(redacted, "[REDACTED_MAC]") {
		t.Errorf("expected [REDACTED_MAC] in output: %s", redacted)
	}
}

func TestRedactSerialAndPaths(t *testing.T) {
	input := "device serial: WD-WCC4N0123456 path /home/john_doe/.cache/driver.ko"
	redacted := RedactEvidence(input)
	if strings.Contains(redacted, "WD-WCC4N0123456") {
		t.Errorf("failed to redact serial number: %s", redacted)
	}
	if strings.Contains(redacted, "john_doe") {
		t.Errorf("failed to redact username from home path: %s", redacted)
	}
}

func TestRedactSecrets(t *testing.T) {
	input := "system token: secret_api_key_1234567890 bearer: my-bearer-token-xyz"
	redacted := RedactEvidence(input)
	if strings.Contains(redacted, "secret_api_key_1234567890") || strings.Contains(redacted, "my-bearer-token-xyz") {
		t.Errorf("failed to redact secrets: %s", redacted)
	}
}

func TestSecurityPolicy(t *testing.T) {
	p := GetPolicy()

	// Protected critical storage driver cannot be unloaded
	canUnload, reason := p.CanUnload("ext4")
	if canUnload {
		t.Errorf("expected ext4 unload to be denied by critical denylist")
	}
	if !strings.Contains(reason, "critical system denylist") {
		t.Errorf("expected denylist reason, got: %s", reason)
	}

	// Normal valid module can be loaded
	canLoad, _ := p.CanLoad("nvidia")
	if !canLoad {
		t.Errorf("expected nvidia load to be allowed")
	}

	// Invalid module format rejected
	canLoadBad, _ := p.CanLoad("bad;module")
	if canLoadBad {
		t.Errorf("expected bad;module load to be rejected")
	}
}
