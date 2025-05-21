# --- Виправлення для GlobalLogic: початок ---
import os, tempfile
cwd = os.getcwd()
tmp = os.path.join(cwd, '.gl_tmp')
os.makedirs(tmp, exist_ok=True)
os.environ['TMPDIR'] = tmp
tempfile.tempdir = tmp
# --- Виправлення для GlobalLogic: кінець --- 