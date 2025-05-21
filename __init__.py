# Хак для тимчасових директорій GlobalLogic
import os

tmp_dir = os.path.join(os.getcwd(), '.tmp')
try:
    os.makedirs(tmp_dir, exist_ok=True)
    # Встановлюємо змінні середовища
    os.environ['TMPDIR'] = tmp_dir
    os.environ['TMP'] = tmp_dir
    os.environ['TEMP'] = tmp_dir
    
    # Патчимо tempfile
    import tempfile
    tempfile.tempdir = tmp_dir
    
    # Перезаписуємо gettempdir
    original_gettempdir = tempfile.gettempdir
    def new_gettempdir():
        return tmp_dir
    tempfile.gettempdir = new_gettempdir
except:
    pass 