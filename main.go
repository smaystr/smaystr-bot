package main

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/smaystr/smaystr-bot/cmd"
)

func init() {
	// Attempt to create tmp directories before any other code executes
	fmt.Println("Creating temporary directories...")

	// Try multiple possible tmp directories
	tmpDirs := []string{
		filepath.Join(".", ".tmp"),
		filepath.Join(".", "tmp"),
		"/tmp",
		"/var/tmp",
		"/usr/tmp",
		"/edx/app/xqwatcher/src/tmp",
	}

	for _, dir := range tmpDirs {
		err := os.MkdirAll(dir, 0777)
		if err != nil {
			fmt.Printf("Failed to create %s: %v\n", dir, err)
		} else {
			err = os.Chmod(dir, 0777)
			if err != nil {
				fmt.Printf("Failed to chmod %s: %v\n", dir, err)
			} else {
				fmt.Printf("Successfully created %s\n", dir)
				// Set environment variables
				os.Setenv("TMPDIR", dir)
				os.Setenv("TMP", dir)
				os.Setenv("TEMP", dir)
				fmt.Printf("Set TMPDIR=%s\n", dir)
				break
			}
		}
	}
}

func main() {
	cmd.Execute()
}
