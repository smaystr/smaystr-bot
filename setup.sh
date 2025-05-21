#!/bin/bash
# CI helper for temporary directories

# Create and export various temp directories
mkdir -p "$PWD/.tmp" && chmod -R 1777 "$PWD/.tmp"
export TMPDIR="$PWD/.tmp"
echo "Created $PWD/.tmp and set TMPDIR=$TMPDIR"

# Try standard locations too
mkdir -p /tmp || mkdir -p tmp || true
chmod 1777 /tmp tmp 2>/dev/null || true

# Allow sourcing this file
echo "export TMPDIR=\"$PWD/.tmp\"" > .tmprc

# Report status
echo "TMPDIR is now $TMPDIR"
echo "Python tempfile.gettempdir() should use: $TMPDIR"

# Verify if Python can create temp files
python3 -c "
import tempfile, os, sys
print('Python temp dir:', tempfile.gettempdir())
try:
    with tempfile.NamedTemporaryFile(delete=True) as f:
        print('Created temp file:', f.name)
        f.write(b'test')
    print('Temp file test: SUCCESS')
except Exception as e:
    print('Error creating temp file:', e)
" 2>/dev/null || echo "Python check skipped - not available"

echo "setup.sh complete" 