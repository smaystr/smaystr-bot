// Helper utility to set up temporary directories for CI/testing
// Usage: go run tools/tmp_setup.go
package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
)

func main() {
	// Get current directory
	wd, err := os.Getwd()
	if err != nil {
		fmt.Printf("Error getting working directory: %v\n", err)
		return
	}

	// Create and set up .tmp directory
	tmpDir := filepath.Join(wd, ".tmp")
	if err := os.MkdirAll(tmpDir, 0777); err != nil {
		fmt.Printf("Error creating .tmp dir: %v\n", err)
	} else {
		fmt.Printf("Created temp directory: %s\n", tmpDir)
		// Set permissions with sticky bit equivalent
		if err := os.Chmod(tmpDir, 0777); err != nil {
			fmt.Printf("Warning: Could not set permissions on %s: %v\n", tmpDir, err)
		}
	}

	// Set environment variables
	os.Setenv("TMPDIR", tmpDir)
	os.Setenv("TEMP", tmpDir)
	os.Setenv("TMP", tmpDir)
	fmt.Printf("Set TMPDIR=%s\n", tmpDir)

	// Also try to create standard /tmp if possible
	if err := os.MkdirAll("/tmp", 0777); err == nil {
		os.Chmod("/tmp", 0777)
		fmt.Println("Created/updated /tmp directory")
	}

	// Create .tmprc for bash
	tmprcContent := fmt.Sprintf("export TMPDIR=\"%s\"\nexport TEMP=\"%s\"\nexport TMP=\"%s\"\n",
		tmpDir, tmpDir, tmpDir)
	if err := ioutil.WriteFile(".tmprc", []byte(tmprcContent), 0644); err != nil {
		fmt.Printf("Warning: Could not create .tmprc: %v\n", err)
	} else {
		fmt.Println("Created .tmprc bash helper")
	}

	// Verify by creating a test file
	testFile := filepath.Join(tmpDir, "test.txt")
	if err := ioutil.WriteFile(testFile, []byte("Test content"), 0644); err != nil {
		fmt.Printf("Error creating test file: %v\n", err)
	} else {
		fmt.Printf("Successfully created test file: %s\n", testFile)
		// Clean up
		os.Remove(testFile)
	}

	fmt.Println("Temporary directory setup complete")
}
