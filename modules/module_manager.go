package modules

import (
	"fmt"
	"log"
	"os/exec"
)

// LoadModule uses modprobe to load a kernel module

func LoadModule(moduleName string) error {
	cmd := exec.Command("modprobe", moduleName)
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Failed to load module: %s, Output: %s", err, string(output))
		return fmt.Errorf("failed to load module: %s", err)
	}
	fmt.Println("Module loaded:", moduleName)
	return nil
}

// UnloadModule uses rmmod to remove a kernel module
func UnloadModule(moduleName string) error {
	cmd := exec.Command("rmmod", moduleName)
	err := cmd.Run()
	if err != nil {
		return fmt.Errorf("failed to unload module: %s", err)
	}
	fmt.Println("Module unloaded:", moduleName)
	return nil
}
