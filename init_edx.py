#!/usr/bin/env python3
# Common entry point for edX grading systems

import os
import sys
import tempfile


def setup_tmp_directories():
    """Set up and configure temporary directories for the grading process."""
    # Create project-local tmp
    local_tmp = os.path.join(os.getcwd(), ".tmp")
    try:
        os.makedirs(local_tmp, exist_ok=True)
        os.chmod(local_tmp, 0o1777)  # world-writable with sticky bit

        # Set environment variables
        os.environ["TMPDIR"] = local_tmp
        os.environ["TEMP"] = local_tmp
        os.environ["TMP"] = local_tmp

        # Force tempfile to use our directory
        tempfile.tempdir = local_tmp

        # Also try system directories
        for system_tmp in ["/tmp", "/var/tmp", "/usr/tmp"]:
            try:
                os.makedirs(system_tmp, exist_ok=True)
                os.chmod(system_tmp, 0o1777)
            except Exception:
                pass

        return True
    except Exception as e:
        sys.stderr.write(f"Error setting up tmp directories: {e}\n")
        return False


# Run setup when imported
result = setup_tmp_directories()
print(f"Init: {'SUCCESS' if result else 'FAILED'}")  # shortened
print(f"Using: {tempfile.gettempdir()}")

# Try to create a test file
try:
    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.write(b"test content")
        print(f"Successfully created test file: {f.name}")
except Exception as e:
    sys.stderr.write(f"Failed to create test file: {e}\n")
