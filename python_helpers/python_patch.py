"""
Direct monkey-patch for Python temporary directories.
This file should be executed by whatever loads your code in the CI system.
"""
import os
import sys
import tempfile

print("CRITICAL: Running Python tmp directory patch")

# Function to check if dir is writable
def test_dir_writable(dirpath):
    if not os.path.isdir(dirpath):
        return False
    try:
        testfile = os.path.join(dirpath, 'test_write_' + str(os.getpid()))
        with open(testfile, 'w') as f:
            f.write('test')
        os.unlink(testfile)
        return True
    except:
        return False

# Try creating all possible tmp directories
for d in ['/tmp', '/var/tmp', '/usr/tmp', '/edx/app/xqwatcher/src/tmp', 
          os.path.join(os.getcwd(), '.tmp'), os.path.join(os.getcwd(), 'tmp')]:
    try:
        os.makedirs(d, exist_ok=True)
        os.chmod(d, 0o1777)  # world-writable with sticky bit
        print(f"Created directory {d}")
    except:
        print(f"Failed to create {d}")

# Set up environment variables for the first working directory
for d in ['/tmp', '/var/tmp', '/usr/tmp', '/edx/app/xqwatcher/src/tmp',
          os.path.join(os.getcwd(), '.tmp'), os.path.join(os.getcwd(), 'tmp')]:
    if test_dir_writable(d):
        print(f"Using {d} as temporary directory")
        os.environ['TMPDIR'] = d
        os.environ['TEMP'] = d
        os.environ['TMP'] = d
        tempfile.tempdir = d
        break
else:
    print("CRITICAL: No writable temp directory found!")

# EXTREME PATCH: Direct monkey-patching of tempfile module
original_gettempdir = tempfile.gettempdir
def patched_gettempdir():
    for d in ['/tmp', '/var/tmp', '/usr/tmp', '/edx/app/xqwatcher/src/tmp',
              os.path.join(os.getcwd(), '.tmp'), os.path.join(os.getcwd(), 'tmp')]:
        if test_dir_writable(d):
            return d
    return original_gettempdir()

tempfile.gettempdir = patched_gettempdir

# Monkeypatch tempfile.mkstemp to always try to use our directory first
original_mkstemp = tempfile.mkstemp
def patched_mkstemp(suffix=None, prefix=None, dir=None, text=False):
    if dir is None:
        dir = patched_gettempdir()
    if test_dir_writable(dir):
        return original_mkstemp(suffix=suffix, prefix=prefix, dir=dir, text=text)
    
    # Fallback to trying specific directories one-by-one
    for d in ['/tmp', '/var/tmp', '/usr/tmp', os.path.join(os.getcwd(), '.tmp')]:
        if test_dir_writable(d):
            return original_mkstemp(suffix=suffix, prefix=prefix, dir=d, text=text)
    
    # Last resort - try the original function
    return original_mkstemp(suffix=suffix, prefix=prefix, dir=dir, text=text)

tempfile.mkstemp = patched_mkstemp

# Test that patching worked
try:
    print(f"Patched tempfile.gettempdir() = {tempfile.gettempdir()}")
    fd, path = tempfile.mkstemp()
    print(f"Successfully created temporary file: {path}")
    os.close(fd)
    os.unlink(path)
except Exception as e:
    print(f"ERROR DURING TESTING: {e}")

print("Python tmp directory patch completed") 