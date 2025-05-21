#!/usr/bin/env python3
# Helper for edX/xqwatcher environment
import os
import sys
import tempfile

# Set up temp directory
tmp_dir = os.path.join(os.getcwd(), '.tmp')
if not os.path.exists(tmp_dir):
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        os.chmod(tmp_dir, 0o1777)  # world-writable with sticky bit
    except Exception as e:
        print(f"Warning: Failed to create {tmp_dir}: {e}", file=sys.stderr)

# Export environment variables
os.environ['TMPDIR'] = tmp_dir
os.environ['TEMP'] = tmp_dir
os.environ['TMP'] = tmp_dir

# Verify
print(f"Python tempfile.gettempdir() now uses: {tempfile.gettempdir()}") 