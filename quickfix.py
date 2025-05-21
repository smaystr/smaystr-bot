# Швидкий фікс тимчасової директорії
import os, tempfile
os.makedirs('.tmp', exist_ok=True)
tempfile.tempdir = os.path.abspath('.tmp')
os.environ['TMPDIR'] = tempfile.tempdir 