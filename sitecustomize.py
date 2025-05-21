#!/usr/bin/env python3
# sitecustomize.py - автоматично завантажується Python при імпорті
import os
import tempfile

print("EDXTMP: Patching temp directories...")

# Список всіх можливих тимчасових директорій
temp_dirs = [
    '/tmp',
    '/var/tmp',
    '/usr/tmp',
    '/edx/app/xqwatcher/src',
    os.path.join(os.getcwd(), '.tmp'),
    os.path.join(os.getcwd(), 'tmp')
]

# Перевіряємо кожну директорію і створюємо якщо потрібно
for dir_path in temp_dirs:
    try:
        os.makedirs(dir_path, mode=0o1777, exist_ok=True)
        os.chmod(dir_path, 0o1777)  # відкриваємо доступ для всіх
        print(f"EDXTMP: Created/ensured {dir_path}")
    except Exception as e:
        print(f"EDXTMP: Failed to create {dir_path}: {e}")

# Знаходимо першу робочу директорію
working_tmp = None
for dir_path in temp_dirs:
    try:
        if os.path.isdir(dir_path) and os.access(dir_path, os.W_OK):
            test_file = os.path.join(dir_path, "test_write_access")
            with open(test_file, 'w') as f:
                f.write('test')
            os.unlink(test_file)
            working_tmp = dir_path
            print(f"EDXTMP: Found working tmp dir: {working_tmp}")
            break
    except Exception as e:
        print(f"EDXTMP: Cannot use {dir_path}: {e}")
        continue

if working_tmp:
    # Патч для tempfile
    print(f"EDXTMP: Patching tempfile to use {working_tmp}")
    tempfile.tempdir = working_tmp
    
    # Встановлюємо змінні середовища
    os.environ['TMPDIR'] = working_tmp
    os.environ['TMP'] = working_tmp
    os.environ['TEMP'] = working_tmp
else:
    print("EDXTMP: WARNING - No working tmp directory found!") 