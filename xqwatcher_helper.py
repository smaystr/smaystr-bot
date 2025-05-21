#!/usr/bin/env python
# xqwatcher environment helper - will be found by edX runner
import os, sys, tempfile

# Print environment information 
print("Current working directory:", os.getcwd())
print("Python version:", sys.version)
print("Environment tmp vars:", os.environ.get('TMPDIR'), os.environ.get('TMP'))

# Create all possible temp directories
try:
    dirs_to_create = [
        os.path.join(os.getcwd(), '.tmp'),
        os.path.join(os.getcwd(), 'tmp'),
        '/tmp',
        '/var/tmp',
        '/usr/tmp',
        '/edx/app/xqwatcher/src/tmp'
    ]
    
    for d in dirs_to_create:
        try:
            os.makedirs(d, exist_ok=True)
            os.chmod(d, 0o1777)  # world-writable with sticky bit
            print(f"Created and set permissions for: {d}")
        except Exception as e:
            print(f"Could not create {d}: {e}", file=sys.stderr)
    
    # Default to a directory we know we can create
    os.environ['TMPDIR'] = os.path.join(os.getcwd(), '.tmp')
    os.environ['TEMP'] = os.environ['TMPDIR']
    os.environ['TMP'] = os.environ['TMPDIR']
    
    # Try to directly monkey-patch tempfile
    tempfile.tempdir = os.environ['TMPDIR']
    
    # Verify 
    try:
        temp_name = tempfile.mktemp()
        with open(temp_name, 'w') as f:
            f.write('test')
        os.unlink(temp_name)
        print(f"Successfully created temp file in {tempfile.gettempdir()}")
    except Exception as e:
        print(f"Error creating temp file: {e}", file=sys.stderr)
except Exception as e:
    print(f"Critical error in xqwatcher_helper.py: {e}", file=sys.stderr) 