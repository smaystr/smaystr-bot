# conftest.py - автоматично використовується pytest
import os
import sys

# Виконати патч для тимчасових директорій
def pytest_configure(config):
    print("GlobalLogic TMP fix (conftest): Running...")
    
    # Створити тимчасову директорію
    tmp_dir = os.path.join(os.getcwd(), '.tmp')
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        print(f"Created directory: {tmp_dir}")
        
        # Встановити змінні середовища
        os.environ['TMPDIR'] = tmp_dir
        os.environ['TMP'] = tmp_dir
        os.environ['TEMP'] = tmp_dir
        
        # Патчимо tempfile
        import tempfile
        tempfile.tempdir = tmp_dir
        
        # Перевіряємо, що працює
        fd, path = tempfile.mkstemp()
        os.close(fd)
        os.unlink(path)
        print(f"GlobalLogic TMP fix (conftest): Using {tmp_dir}")
        
    except Exception as e:
        print(f"GlobalLogic TMP fix (conftest): ERROR - {e}") 