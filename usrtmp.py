#!/usr/bin/env python3
"""
Extreme monkey patching of tempfile module via sys.modules
This gets imported early in the edX check process
"""
import os
import sys

# Create tmp directories
os.makedirs(os.path.join(os.getcwd(), ".tmp"), exist_ok=True)
os.chmod(os.path.join(os.getcwd(), ".tmp"), 0o1777)

# Try to create standard directories
for d in ["/tmp", "/var/tmp", "/usr/tmp", "/edx/app/xqwatcher/src/tmp"]:
    try:
        os.makedirs(d, exist_ok=True)
        os.chmod(d, 0o1777)
        print(f"Created {d}")
    except:
        print(f"Failed to create {d}")

# Define our patched tempfile module
class FakeTempfileModule:
    """Fake tempfile module that always uses a working tmp directory"""
    
    def __init__(self):
        self.tempdir = os.path.join(os.getcwd(), ".tmp")
        self._orig_module = None
        
        # Set environment variables too
        os.environ["TMPDIR"] = self.tempdir
        os.environ["TEMP"] = self.tempdir
        os.environ["TMP"] = self.tempdir
        
        print(f"FakeTempfileModule initialized with tempdir={self.tempdir}")
    
    def __getattr__(self, name):
        """Pass through to real module but enforce our tempdir"""
        import tempfile
        self._orig_module = tempfile
        
        # Get the original attribute
        orig_attr = getattr(tempfile, name)
        
        # If it's a function, we might need to fix its behavior
        if callable(orig_attr):
            # For simple functions, just return them
            return orig_attr
            
        return orig_attr
    
    # Override critical functions to enforce our tempdir
    def gettempdir(self):
        return self.tempdir
        
    def mkstemp(self, suffix="", prefix="tmp", dir=None, text=False):
        """Force dir to our tempdir"""
        import tempfile
        return tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=self.tempdir, text=text)
    
    def mkdtemp(self, suffix="", prefix="tmp", dir=None):
        """Force dir to our tempdir"""
        import tempfile
        return tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=self.tempdir)
    
    def TemporaryFile(self, *args, **kwargs):
        """Force dir to our tempdir"""
        import tempfile
        kwargs['dir'] = self.tempdir
        return tempfile.TemporaryFile(*args, **kwargs)
    
    def NamedTemporaryFile(self, *args, **kwargs):
        """Force dir to our tempdir"""
        import tempfile
        kwargs['dir'] = self.tempdir
        return tempfile.NamedTemporaryFile(*args, **kwargs)

# Try to monkey patch sys.modules directly
try:
    # Only replace if not already imported
    if 'tempfile' not in sys.modules:
        print("Monkey patching tempfile module before import")
        sys.modules['tempfile'] = FakeTempfileModule()
    else:
        print("tempfile already imported, applying direct monkey patching")
        sys.modules['tempfile'].tempdir = os.path.join(os.getcwd(), ".tmp")
        orig_gettempdir = sys.modules['tempfile'].gettempdir
        sys.modules['tempfile'].gettempdir = lambda: os.path.join(os.getcwd(), ".tmp")
        print(f"Patched gettempdir: {orig_gettempdir()} -> {sys.modules['tempfile'].gettempdir()}")
except Exception as e:
    print(f"Failed to monkey patch tempfile: {e}")

print("usrtmp.py: monkey patching completed") 