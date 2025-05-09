package cmd

import (
	"os"
	"testing"

	"github.com/stretchr/testify/require"
)

// TestRootCmd_NoToken ensures Execute fails when TELE_TOKEN is not set.
func TestRootCmd_NoToken(t *testing.T) {
	// Backup and defer restore
	original := os.Getenv("TELE_TOKEN")
	_ = os.Unsetenv("TELE_TOKEN")
	if original != "" {
		t.Cleanup(func() { _ = os.Setenv("TELE_TOKEN", original) })
	}

	// Execute root command directly to capture error instead of log.Fatal.
	err := rootCmd.Execute()
	require.Error(t, err)
	require.Contains(t, err.Error(), "TELE_TOKEN")
}
