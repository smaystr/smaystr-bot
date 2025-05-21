"""
TempFile configuration for edX
"""
import os
import sys
import tempfile

# Create tmp directories
cwd = os.getcwd()
tmp_dirs = [
    os.path.join(cwd, '.tmp'),
    os.path.join(cwd, 'tmp'),
    '/tmp',
    '/var/tmp',
    '/edx/app/xqwatcher/src/tmp'
]

# Create directories and set up environment
for dir_path in tmp_dirs:
    try:
        os.makedirs(dir_path, exist_ok=True)
        os.chmod(dir_path, 0o1777)
        print(f"Created {dir_path} with correct permissions")
        
        # Set first successful dir as TMPDIR
        if not os.environ.get('TMPDIR'):
            os.environ['TMPDIR'] = dir_path
            os.environ['TEMP'] = dir_path
            os.environ['TMP'] = dir_path
            tempfile.tempdir = dir_path
            print(f"Set TMPDIR to {dir_path}")
            
            # Test it
            test_file = tempfile.mktemp()
            with open(test_file, 'w') as f:
                f.write('test')
            os.unlink(test_file)
            print(f"Successfully created and verified temp file in {dir_path}")
            break
    except Exception as e:
        print(f"Failed to set up {dir_path}: {e}", file=sys.stderr)
        continue

# Report final status
print(f"tempfile.gettempdir() = {tempfile.gettempdir()}")
