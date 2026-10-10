package modules

import (
	"os"
	"testing"
)

func TestDemoModeEvidence(t *testing.T) {
	orig := os.Getenv("DEMO_MODE")
	defer os.Setenv("DEMO_MODE", orig)

	os.Setenv("DEMO_MODE", "true")
	if !IsDemoMode() {
		t.Fatalf("expected IsDemoMode to be true")
	}

	// Test canned fixture for nvidia
	ev := Diagnose("nvidia")
	if ev.Module != "nvidia" {
		t.Errorf("expected module nvidia, got %s", ev.Module)
	}
	if ev.Commands["uname"] == "" {
		t.Errorf("expected uname in canned evidence")
	}
	if ev.Errors["modprobe"] == "" {
		t.Errorf("expected modprobe error in canned nvidia fixture")
	}

	// Test canned fixture for healthy loop
	loopEv := Diagnose("loop")
	if loopEv.Module != "loop" {
		t.Errorf("expected loop, got %s", loopEv.Module)
	}
	if len(loopEv.Errors) != 0 {
		t.Errorf("expected no errors for healthy loop module, got %v", loopEv.Errors)
	}

	// Test default fallback for unseen module
	defaultEv := Diagnose("random_custom_mod")
	if defaultEv.Module != "random_custom_mod" {
		t.Errorf("expected random_custom_mod, got %s", defaultEv.Module)
	}
	if defaultEv.Commands["uname"] == "" {
		t.Errorf("expected default canned commands")
	}

	// Test simulated load/unload
	if err := LoadModule("nvidia"); err != nil {
		t.Errorf("expected demo LoadModule to succeed, got %v", err)
	}
	if err := UnloadModule("nvidia"); err != nil {
		t.Errorf("expected demo UnloadModule to succeed, got %v", err)
	}
}
