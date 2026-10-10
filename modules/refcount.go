package modules

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

// IsModuleInUse checks /proc/modules or lsmod output to determine if a module has refcount > 0.
func IsModuleInUse(moduleName string) (bool, int, []string, error) {
	// 1. Try reading /proc/modules directly if available
	f, err := os.Open("/proc/modules")
	if err == nil {
		defer f.Close()
		scanner := bufio.NewScanner(f)
		for scanner.Scan() {
			fields := strings.Fields(scanner.Text())
			if len(fields) >= 3 && fields[0] == moduleName {
				refCount, _ := strconv.Atoi(fields[2])
				usedBy := []string{}
				if len(fields) >= 4 && fields[3] != "-" {
					usedBy = strings.Split(strings.TrimSuffix(fields[3], ","), ",")
				}
				return refCount > 0, refCount, usedBy, nil
			}
		}
		return false, 0, nil, nil
	}

	// 2. Fallback: Parse lsmod output via evidence
	evidence := Diagnose(moduleName)
	lsmodOut := evidence.Commands["lsmod"]
	lines := strings.Split(lsmodOut, "\n")
	for _, line := range lines {
		fields := strings.Fields(line)
		if len(fields) >= 3 && fields[0] == moduleName {
			refCount, _ := strconv.Atoi(fields[2])
			usedBy := []string{}
			if len(fields) >= 4 {
				usedBy = strings.Split(fields[3], ",")
			}
			return refCount > 0, refCount, usedBy, nil
		}
	}

	return false, 0, nil, fmt.Errorf("module %s not found in loaded module list", moduleName)
}
