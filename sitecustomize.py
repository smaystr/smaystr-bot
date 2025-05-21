"""
Python automatically imports this module on startup.
It's designed to fix temporary directory issues for edX/testing environments.
"""
import os
import sys
import tempfile

# Log that we're running
print("sitecustomize.py: Starting automatic tempdir fix")

# Create and use a list of possible temporary directories
def setup_tempdir():
    possible_dirs = [
        # Current directory tmp options
        os.path.join(os.getcwd(), ".tmp"),
        os.path.join(os.getcwd(), "tmp"),
        # Standard system directories
        "/tmp", 
        "/var/tmp",
        "/usr/tmp",
        # edX specific paths
        "/edx/app/xqwatcher/src/tmp",
        "/edx/tmp",
        # Home directory
        os.path.expanduser("~/tmp")
    ]
    
    # Try to create and use each directory
    for dir_path in possible_dirs:
        try:
            # Create directory with world-writable permissions
            os.makedirs(dir_path, exist_ok=True)
            os.chmod(dir_path, 0o1777)  # rwxrwxrwt - world writable with sticky bit
            
            # Set as environment variables
            os.environ["TMPDIR"] = dir_path
            os.environ["TEMP"] = dir_path
            os.environ["TMP"] = dir_path
            
            # CRITICAL: Directly patch tempfile module
            tempfile.tempdir = dir_path
            
            # Verify it works by creating a test file
            test_fd, test_path = tempfile.mkstemp(prefix="test_")
            os.close(test_fd)
            os.unlink(test_path)
            
            print(f"sitecustomize.py: Successfully set up temp directory: {dir_path}")
            print(f"sitecustomize.py: tempfile.gettempdir() = {tempfile.gettempdir()}")
            return True
        except Exception as e:
            print(f"sitecustomize.py: Failed to set up {dir_path}: {e}", file=sys.stderr)
    
    # If we get here, none of the directories worked
    print("sitecustomize.py: CRITICAL - Could not find any usable temp directory", file=sys.stderr)
    return False

# Run the setup immediately on import
setup_tempdir() 