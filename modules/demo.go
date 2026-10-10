package modules

import (
	"embed"
	"encoding/json"
	"os"
	"strings"
)

//go:embed fixtures/*.json
var demoFixtures embed.FS

// IsDemoMode checks if DEMO_MODE environment variable is active.
func IsDemoMode() bool {
	v := strings.ToLower(strings.TrimSpace(os.Getenv("DEMO_MODE")))
	return v == "true" || v == "1" || v == "yes"
}

// GetDemoEvidence returns a canned Evidence struct from embedded fixtures for macOS/Windows/demo runs.
func GetDemoEvidence(name string) Evidence {
	safeName := strings.ToLower(strings.TrimSpace(name))
	fixturePath := "fixtures/" + safeName + ".json"

	data, err := demoFixtures.ReadFile(fixturePath)
	if err != nil {
		// Fallback to default fixture
		data, err = demoFixtures.ReadFile("fixtures/default.json")
		if err != nil {
			// Minimal in-memory fallback
			return Evidence{
				Module: name,
				Commands: map[string]string{
					"uname": "6.8.0-40-generic",
					"lsmod": "",
					"dmesg": "[DEMO MODE] Simulated diagnostic evidence for module: " + name,
				},
				Errors: map[string]string{
					"modprobe": "modprobe: FATAL: Module " + name + " not found (demo mode)",
				},
			}
		}
	}

	var ev Evidence
	if err := json.Unmarshal(data, &ev); err != nil {
		return Evidence{
			Module: name,
			Commands: map[string]string{
				"uname": "6.8.0-40-generic",
				"dmesg": "[DEMO MODE] Fallback evidence",
			},
		}
	}

	// Ensure the module name matches the requested module
	ev.Module = name
	return ev
}
