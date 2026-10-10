package modules

import (
	"bufio"
	"os"
	"strings"
	"sync"
)

// SecurityPolicy defines allowlist and denylist constraints.
type SecurityPolicy struct {
	DenyByDefault    bool
	AllowedModules   map[string]bool
	CriticalDenylist map[string]bool
	mu               sync.RWMutex
}

var (
	defaultPolicy *SecurityPolicy
	policyOnce    sync.Once
)

// Hardcoded critical denylist protecting essential storage and filesystem drivers
var defaultCriticalDenylist = map[string]bool{
	"ext4":      true,
	"btrfs":     true,
	"xfs":       true,
	"vfat":      true,
	"zfs":       true,
	"nvme":      true,
	"nvme_core": true,
	"ahci":      true,
	"libahci":   true,
	"sd_mod":    true,
	"dm_mod":    true,
}

// GetPolicy returns the active security policy, loading policy.yaml if present.
func GetPolicy() *SecurityPolicy {
	policyOnce.Do(func() {
		defaultPolicy = &SecurityPolicy{
			DenyByDefault:    false,
			AllowedModules:   make(map[string]bool),
			CriticalDenylist: make(map[string]bool),
		}
		for k, v := range defaultCriticalDenylist {
			defaultPolicy.CriticalDenylist[k] = v
		}
		// Attempt loading policy.yaml from current dir or env
		policyPath := os.Getenv("POLICY_FILE")
		if policyPath == "" {
			policyPath = "policy.yaml"
		}
		_ = loadPolicyFile(defaultPolicy, policyPath)
	})
	return defaultPolicy
}

func loadPolicyFile(p *SecurityPolicy, path string) error {
	f, err := os.Open(path)
	if err != nil {
		return err
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	currentSection := ""

	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		if strings.HasPrefix(line, "deny_by_default:") {
			val := strings.TrimSpace(strings.TrimPrefix(line, "deny_by_default:"))
			p.DenyByDefault = strings.EqualFold(val, "true")
			continue
		}
		if strings.HasSuffix(line, ":") {
			currentSection = strings.TrimSuffix(line, ":")
			continue
		}
		if strings.HasPrefix(line, "-") {
			item := strings.TrimSpace(strings.TrimPrefix(line, "-"))
			if currentSection == "allowed_modules" {
				p.AllowedModules[item] = true
			} else if currentSection == "critical_denylist" {
				p.CriticalDenylist[item] = true
			}
		}
	}
	return scanner.Err()
}

// CanLoad evaluates whether a module name passes both regex validation and security policy.
func (p *SecurityPolicy) CanLoad(module string) (bool, string) {
	if !ValidModule(module) {
		return false, "invalid module name format"
	}
	p.mu.RLock()
	defer p.mu.RUnlock()

	if p.DenyByDefault && !p.AllowedModules[module] {
		return false, "module not in allowed policy list"
	}
	return true, ""
}

// CanUnload evaluates whether a module is permitted to be unloaded (not in critical denylist).
func (p *SecurityPolicy) CanUnload(module string) (bool, string) {
	if !ValidModule(module) {
		return false, "invalid module name format"
	}
	p.mu.RLock()
	defer p.mu.RUnlock()

	if p.CriticalDenylist[module] {
		return false, "module is protected by critical system denylist"
	}
	if p.DenyByDefault && !p.AllowedModules[module] {
		return false, "module not in allowed policy list"
	}
	return true, ""
}
