#!/bin/bash
# Wrapper script to initialize temporary directories before running any command
# Usage: ./start_with_tmp.sh <command_to_run>

set -e

echo "Running temporary directory setup..."

# Try to create all possible temporary directories
for dir in "/tmp" "/var/tmp" "/usr/tmp" "/edx/app/xqwatcher/src/tmp" ".tmp" "tmp"; do
    mkdir -p "$dir" 2>/dev/null || true
    chmod -R 1777 "$dir" 2>/dev/null || true
    echo "Tried to create $dir"
done

# Export environment variables
export TMPDIR="/tmp"
export TMP="/tmp"
export TEMP="/tmp"
export TEMPDIR="/tmp"
export PYTHON_EGG_CACHE="/tmp"

# Run the Python patcher
python3 python_patch.py || python python_patch.py || echo "Failed to run python patch"

# Execute the original command with all arguments
echo "Running original command: $@"
exec "$@" 