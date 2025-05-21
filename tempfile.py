"""
Direct replacement for the tempfile module that works around permission issues
"""
import os
import sys
import random
import io
from typing import Any

# Create and ensure our temp directory exists
TEMPDIR = os.path.join(os.getcwd(), ".tmp")
os.makedirs(TEMPDIR, exist_ok=True)
os.chmod(TEMPDIR, 0o1777)  # rwxrwxrwt

# Set environment variables
os.environ["TMPDIR"] = TEMPDIR
os.environ["TEMP"] = TEMPDIR
os.environ["TMP"] = TEMPDIR

# For debugging
print(f"Using custom tempfile.py with TEMPDIR={TEMPDIR}")

# Import the real tempfile for delegation
_real_tempfile = None
try:
    # Import the actual tempfile without triggering infinite recursion
    import importlib.machinery
    import importlib.util

    # Find the real tempfile module
    for path in sys.path:
        loader = None
        module_path = os.path.join(path, "tempfile.py")
        
        # Skip our own file
        if module_path == __file__:
            continue
            
        if os.path.exists(module_path):
            loader = importlib.machinery.SourceFileLoader("real_tempfile", module_path)
            spec = importlib.util.spec_from_loader("real_tempfile", loader)
            _real_tempfile = importlib.util.module_from_spec(spec)
            
            # Save the original tempdir
            original_tempdir = os.environ.get("TMPDIR")
            os.environ["TMPDIR"] = TEMPDIR
            
            # Load the module
            loader.exec_module(_real_tempfile)
            
            # Restore the original tempdir if it existed
            if original_tempdir:
                os.environ["TMPDIR"] = original_tempdir
            
            break
except Exception as e:
    print(f"Error importing real tempfile: {e}")
    pass

# Fallback to minimal implementation if we couldn't import
if _real_tempfile is None:
    print("WARNING: Using minimal tempfile implementation")
    
    # Define minimal functions
    def _mktemp(*args, **kwargs):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789_"
        letters = [random.choice(chars) for _ in range(8)]
        random_part = "".join(letters)
        return os.path.join(TEMPDIR, f"tmp_{random_part}")
    
    # Constants
    template = "tmp"
    tempdir = TEMPDIR
    gettempdir = lambda: TEMPDIR
    
    def mkstemp(suffix="", prefix="tmp", dir=None, text=False):
        if dir is None:
            dir = TEMPDIR
        name = _mktemp(dir=dir, prefix=prefix, suffix=suffix)
        fd = os.open(name, os.O_RDWR | os.O_CREAT | os.O_EXCL)
        return fd, name
    
    def mkdtemp(suffix="", prefix="tmp", dir=None):
        if dir is None:
            dir = TEMPDIR
        name = _mktemp(dir=dir, prefix=prefix, suffix=suffix)
        os.mkdir(name)
        return name
        
    def TemporaryFile(*args, **kwargs):
        return io.BytesIO()
        
    def NamedTemporaryFile(*args, **kwargs):
        fd, name = mkstemp()
        os.close(fd)
        return open(name, "wb+")
else:
    # Use functions from real tempfile but override tempdir
    globals().update(_real_tempfile.__dict__)
    tempdir = TEMPDIR
    _real_tempfile.tempdir = TEMPDIR
    
    # Override gettempdir
    def gettempdir():
        return TEMPDIR
    
    # For safety, override other key functions that might use a different directory
    _orig_mkstemp = _real_tempfile.mkstemp
    def mkstemp(suffix="", prefix="tmp", dir=None, text=False):
        return _orig_mkstemp(suffix=suffix, prefix=prefix, dir=TEMPDIR, text=text)
    
    _orig_mkdtemp = _real_tempfile.mkdtemp
    def mkdtemp(suffix="", prefix="tmp", dir=None):
        return _orig_mkdtemp(suffix=suffix, prefix=prefix, dir=TEMPDIR)
    
    # Override the class based APIs too
    if hasattr(_real_tempfile, 'TemporaryFile'):
        _orig_TemporaryFile = _real_tempfile.TemporaryFile
        def TemporaryFile(*args, **kwargs):
            kwargs['dir'] = TEMPDIR
            return _orig_TemporaryFile(*args, **kwargs)
    
    if hasattr(_real_tempfile, 'NamedTemporaryFile'):
        _orig_NamedTemporaryFile = _real_tempfile.NamedTemporaryFile
        def NamedTemporaryFile(*args, **kwargs):
            kwargs['dir'] = TEMPDIR
            return _orig_NamedTemporaryFile(*args, **kwargs) 