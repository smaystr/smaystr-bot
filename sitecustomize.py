"""
sitecustomize.py - цей файл автоматично імпортується Python при запуску
Розмістіть його в корені репозиторію
"""
import os
import sys
import atexit

# Додаємо поточну директорію в PYTHONPATH
sys.path.insert(0, os.getcwd())

print("GlobalLogic TMP fix: Initializing...")

# Створюємо тимчасову директорію в поточній директорії
tmp_dir = os.path.join(os.getcwd(), '.tmp')
try:
    os.makedirs(tmp_dir, exist_ok=True)
    print(f"GlobalLogic TMP fix: Created directory {tmp_dir}")
    
    # Встановлюємо змінні середовища
    os.environ['TMPDIR'] = tmp_dir
    os.environ['TMP'] = tmp_dir
    os.environ['TEMP'] = tmp_dir
    
    # Патчимо tempfile
    import tempfile
    tempfile.tempdir = tmp_dir
    
    # Заміна функції gettempdir
    orig_gettempdir = tempfile.gettempdir
    def patched_gettempdir():
        return tmp_dir
    tempfile.gettempdir = patched_gettempdir
    
    # Тест
    test_fd, test_path = tempfile.mkstemp()
    os.close(test_fd)
    os.unlink(test_path)
    print(f"GlobalLogic TMP fix: Successfully patched tempfile, using {tmp_dir}")
    
    # Функція очищення при завершенні
    def cleanup():
        try:
            import shutil
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)
                print(f"GlobalLogic TMP fix: Cleaned up {tmp_dir}")
        except:
            pass
    
    atexit.register(cleanup)
    
except Exception as e:
    print(f"GlobalLogic TMP fix: ERROR setting up tmp directory: {e}")
