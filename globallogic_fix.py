#!/usr/bin/env python3
"""
НАДПОТУЖНИЙ ФІКС ДЛЯ GLOBALLOGIC

1. Додайте в корінь репозиторію
2. Імпортуйте на самому початку тестового скрипта:
   import globallogic_fix

3. АБО просто вставте цей код на початку тестового файлу.
"""
import os
import sys

# Встановлюємо широкий набір змінних середовища
def set_tmp_env():
    tmp_dir = os.path.abspath(os.path.join(os.getcwd(), '.gl_tmp'))
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        for var in ['TMPDIR', 'TMP', 'TEMP', 'TEMPDIR', 'PYTHON_EGG_CACHE']:
            os.environ[var] = tmp_dir
        return tmp_dir
    except Exception as e:
        print(f"ПОМИЛКА встановлення змінних середовища: {e}")
        return None

# Гарантуємо існування директорії для тимчасових файлів
TMP_DIR = set_tmp_env()
print(f"GlobalLogic Fix: Встановлено тимчасову директорію {TMP_DIR}")

# Патчимо стандартні модулі Python ще до їх імпорту 
def patch_tempfile_module():
    try:
        import tempfile
        # Зберігаємо оригінальні функції
        orig_gettempdir = tempfile.gettempdir
        orig_mkstemp = tempfile.mkstemp
        orig_mkdtemp = tempfile.mkdtemp
        
        # Встановлюємо нашу директорію напряму
        tempfile.tempdir = TMP_DIR
        
        # Перевизначаємо основні функції
        def patched_gettempdir():
            return TMP_DIR
            
        def patched_mkstemp(suffix=None, prefix=None, dir=None, text=False):
            if dir is None:
                dir = TMP_DIR
            return orig_mkstemp(suffix=suffix, prefix=prefix, dir=dir, text=text)
            
        def patched_mkdtemp(suffix=None, prefix=None, dir=None):
            if dir is None:
                dir = TMP_DIR
            return orig_mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
        
        # Застосовуємо наші функції
        tempfile.gettempdir = patched_gettempdir
        tempfile.mkstemp = patched_mkstemp
        tempfile.mkdtemp = patched_mkdtemp
        
        # Тестуємо
        test_fd, test_path = tempfile.mkstemp()
        os.close(test_fd)
        os.unlink(test_path)
        print(f"GlobalLogic Fix: tempfile успішно пропатчено, тест пройдено")
        
        # Патчимо модуль os для tempnam
        if hasattr(os, 'tempnam'):
            orig_tempnam = os.tempnam
            def patched_tempnam(dir=None, prefix=None):
                return orig_tempnam(TMP_DIR, prefix)
            os.tempnam = patched_tempnam
    except Exception as e:
        print(f"GlobalLogic Fix: Помилка патчу tempfile: {e}")

# Застосовуємо патч до tempfile
patch_tempfile_module()

# Перехоплюємо всі імпорти для tempfile
import builtins
_original_import = builtins.__import__

def _patched_import(name, globals=None, locals=None, fromlist=(), level=0):
    # Імпортуємо оригінальний модуль
    module = _original_import(name, globals, locals, fromlist, level)
    
    # Якщо це tempfile - патчимо
    if name == 'tempfile' or name.endswith('.tempfile'):
        # Встановлюємо нашу директорію для tempfile
        module.tempdir = TMP_DIR
        
        # Перезаписуємо метод gettempdir
        def new_gettempdir():
            return TMP_DIR
        module.gettempdir = new_gettempdir
        
        print(f"GlobalLogic Fix: Перехоплено імпорт tempfile")
    
    return module

# Встановлюємо перехоплювач імпортів
builtins.__import__ = _patched_import

print("GlobalLogic Fix: Система підготовлена для роботи з тимчасовими файлами")
print(f"GlobalLogic Fix: Використовується директорія: {TMP_DIR}")
sys.stderr.write(f"GlobalLogic Fix: stderr - тимчасова директорія: {TMP_DIR}\n") 