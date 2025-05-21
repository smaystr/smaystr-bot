#!/usr/bin/env python3
# usrtmp.py - патч для модифікації sys.modules['tempfile']

import os
import sys

print("EDXTMP: Running usrtmp.py patch...")

# Створюємо всі можливі тимчасові директорії
tmp_dirs = [
    '/tmp',
    '/var/tmp',
    '/usr/tmp',
    '/edx/app/xqwatcher/src',
    '/edx/app/xqwatcher/src/tmp',
    os.path.join(os.getcwd(), '.tmp'),
    os.path.join(os.getcwd(), 'tmp')
]

# Створюємо директорії з правильними правами
for dir_path in tmp_dirs:
    try:
        os.makedirs(dir_path, mode=0o1777, exist_ok=True)
        os.chmod(dir_path, 0o1777)  # відкриваємо доступ для всіх
        print(f"EDXTMP: Created directory: {dir_path}")
    except Exception as e:
        print(f"EDXTMP: Failed to create {dir_path}: {e}")

# Знаходимо першу робочу тимчасову директорію
working_dir = None
for dir_path in tmp_dirs:
    try:
        if os.path.isdir(dir_path) and os.access(dir_path, os.W_OK):
            test_file = os.path.join(dir_path, "test_writable_tmp")
            with open(test_file, 'w') as f:
                f.write('test')
            os.unlink(test_file)
            working_dir = dir_path
            print(f"EDXTMP: Found working directory: {working_dir}")
            break
    except Exception as e:
        print(f"EDXTMP: Cannot use {dir_path}: {e}")
        continue

if working_dir:
    # Модифікуємо змінні середовища
    os.environ['TMPDIR'] = working_dir
    os.environ['TMP'] = working_dir
    os.environ['TEMP'] = working_dir

    # Патчимо tempfile, якщо він вже завантажений
    try:
        import tempfile
        tempfile.tempdir = working_dir
    
        # Перевизначаємо gettempdir
        orig_gettempdir = tempfile.gettempdir
        def new_gettempdir():
            return working_dir
        tempfile.gettempdir = new_gettempdir
        
        print(f"EDXTMP: Patched tempfile.gettempdir to use {working_dir}")
        
        # Перевіряємо, що працює
        try:
            fd, path = tempfile.mkstemp()
            os.close(fd)
            os.unlink(path)
            print(f"EDXTMP: Test tempfile creation successful")
        except Exception as e:
            print(f"EDXTMP: Test tempfile creation failed: {e}")
    except ImportError:
        print("EDXTMP: tempfile not imported yet, will use environment variables")
    
    print(f"EDXTMP: Temp directory setup complete: {working_dir}")
else:
    print("EDXTMP: WARNING - No working temp directory found!")

# Функція для виклику в інших модулях
def ensure_tmp_dir():
    return working_dir

# Для прямого імпорту
if __name__ == "__main__":
    print(f"EDXTMP: Working dir: {working_dir}")

# Експортуємо необхідні змінні
__all__ = ['ensure_tmp_dir', 'working_dir'] 