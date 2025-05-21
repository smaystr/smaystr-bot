# FIX: No usable temporary directory
import os, tempfile
_tmp = os.path.join(os.getcwd(), '.tmp')
os.makedirs(_tmp, exist_ok=True)
os.environ['TMPDIR'] = _tmp
os.environ['TEMP'] = _tmp
os.environ['TMP'] = _tmp
tempfile.tempdir = _tmp 