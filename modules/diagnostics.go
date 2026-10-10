package modules

import (
	"context"
	"os/exec"
	"regexp"
	"strings"
	"time"
)

var validModule = regexp.MustCompile(`^[a-zA-Z0-9_][a-zA-Z0-9_-]{0,127}$`)

// ValidModule validates module name against safe alphanumeric format.
func ValidModule(name string) bool { return validModule.MatchString(name) }

// Evidence holds command outputs and errors collected from the host system.
type Evidence struct {
	Module   string            `json:"module"`
	Commands map[string]string `json:"commands"`
	Errors   map[string]string `json:"errors,omitempty"`
}

// Diagnose gathers diagnostic command outputs, runs without subshells where possible,
// truncates buffers, and redacts sensitive internal data (IPs, MACs, secrets, paths).
func Diagnose(name string) Evidence {
	e := Evidence{Module: name, Commands: map[string]string{}, Errors: map[string]string{}}
	if !ValidModule(name) {
		e.Errors["validation"] = "invalid module name"
		return e
	}

	if IsDemoMode() {
		return GetDemoEvidence(name)
	}

	specs := []struct {
		key  string
		prog string
		args []string
	}{
		{"uname", "uname", []string{"-r"}},
		{"lsmod", "lsmod", []string{}},
		{"modinfo", "modinfo", []string{name}},
		{"dmesg", "dmesg", []string{}},
		{"journalctl", "journalctl", []string{"-k", "--no-pager", "-n", "30"}},
		{"modprobe_deps", "modprobe", []string{"--show-depends", name}},
	}

	for _, spec := range specs {
		ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
		cmd := exec.CommandContext(ctx, spec.prog, spec.args...)
		out, err := cmd.CombinedOutput()
		cancel()

		result := strings.TrimSpace(string(out))
		if spec.key == "dmesg" {
			// Keep tail 50 lines cleanly in Go without shell pipe
			lines := strings.Split(result, "\n")
			if len(lines) > 50 {
				lines = lines[len(lines)-50:]
			}
			result = strings.Join(lines, "\n")
		}

		if len(result) > 12000 {
			result = result[:12000] + "...[truncated]"
		}

		// Apply security redaction before storing evidence
		e.Commands[spec.key] = RedactEvidence(result)
		if err != nil {
			e.Errors[spec.key] = err.Error()
		}
	}
	return e
}
