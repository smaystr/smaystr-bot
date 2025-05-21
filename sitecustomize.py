#!/usr/bin/env python3
# sitecustomize.py - автоматично завантажується Python при імпорті
import os
import sys
import tempfile
import stat
import importlib
import builtins

print("EDXTMP: Patching temp directories (EMERGENCY OVERRIDE)...")

# Перехоплюємо імпорти на рівні Python
original_import = builtins.__import__

def patched_import(name, *args, **kwargs):
    module = original_import(name, *args, **kwargs)
    
    # Перехоплюємо tempfile
    if name == 'tempfile':
        patch_tempfile(module)
    
    return module

# Заміняємо стандартний __import__
builtins.__import__ = patched_import

# Список всіх можливих тимчасових директорій
temp_dirs = [
    '/tmp',
    '/var/tmp',
    '/usr/tmp',
    '/edx/app/xqwatcher/src',
    '/edx/app/xqwatcher/src/tmp',
    os.path.join(os.getcwd(), '.tmp'),
    os.path.join(os.getcwd(), 'tmp'),
    '/dev/shm',
    '/run/shm',
    '/app',
    '.',
    os.getcwd(),
    os.path.expanduser('~'),
]

# Створюємо всі можливі директорії
for dir_path in temp_dirs:
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, mode=0o1777, exist_ok=True)
        
        # Встановлюємо максимальні права доступу
        try:
            os.chmod(dir_path, 0o1777)  # відкриваємо доступ для всіх
        except:
            pass
            
        print(f"EDXTMP: Created/ensured {dir_path}")
    except Exception as e:
        print(f"EDXTMP: Failed to create {dir_path}: {e}")

# Знаходимо першу робочу директорію
working_tmp = None
for dir_path in temp_dirs:
    try:
        if os.path.isdir(dir_path):
            try:
                # Перевіряємо доступ на запис
                os.access(dir_path, os.W_OK)
                
                # Додаткова перевірка через файл
                test_file = os.path.join(dir_path, "test_write_access")
                with open(test_file, 'w') as f:
                    f.write('test')
                os.unlink(test_file)
                
                working_tmp = dir_path
                print(f"EDXTMP: Found working tmp dir: {working_tmp}")
                break
            except Exception as e:
                print(f"EDXTMP: Cannot use {dir_path} for writing: {e}")
    except Exception as e:
        print(f"EDXTMP: Cannot access {dir_path}: {e}")
        continue

# Якщо не знайшли жодної робочої директорії, створюємо свою в поточній директорії
if not working_tmp:
    try:
        fallback_dir = os.path.join(os.getcwd(), '.tmp_fallback')
        os.makedirs(fallback_dir, mode=0o777, exist_ok=True)
        os.chmod(fallback_dir, 0o777)  # максимально відкритий доступ
        
        test_file = os.path.join(fallback_dir, "test_write")
        with open(test_file, 'w') as f:
            f.write('test')
        os.unlink(test_file)
        
        working_tmp = fallback_dir
        print(f"EDXTMP: Using fallback directory: {working_tmp}")
    except Exception as e:
        print(f"EDXTMP: Failed to create fallback dir: {e}")

# Патчимо модуль tempfile
def patch_tempfile(module):
    if working_tmp:
        print(f"EDXTMP: Patching tempfile module to use {working_tmp}")
        
        # Встановлюємо нашу тимчасову директорію
        module.tempdir = working_tmp
        
        # Перевизначаємо gettempdir
        original_gettempdir = module.gettempdir
        def new_gettempdir():
            return working_tmp
        module.gettempdir = new_gettempdir
        
        # Патчимо інші методи, які можуть використовувати тимчасові директорії
        original_mkstemp = module.mkstemp
        def new_mkstemp(suffix=None, prefix=None, dir=None, text=False):
            return original_mkstemp(suffix, prefix, working_tmp, text)
        module.mkstemp = new_mkstemp
        
        original_mkdtemp = module.mkdtemp
        def new_mkdtemp(suffix=None, prefix=None, dir=None):
            return original_mkdtemp(suffix, prefix, working_tmp)
        module.mkdtemp = new_mkdtemp
        
        # Перевірка, що патч працює
        try:
            fd, path = module.mkstemp()
            os.close(fd)
            os.unlink(path)
            print(f"EDXTMP: Successfully created test file at {path}")
        except Exception as e:
            print(f"EDXTMP: Test file creation failed: {e}")

if working_tmp:
    # Патч для tempfile, якщо він вже завантажений
    if 'tempfile' in sys.modules:
        patch_tempfile(sys.modules['tempfile'])
    
    # Встановлюємо змінні середовища
    os.environ['TMPDIR'] = working_tmp
    os.environ['TMP'] = working_tmp
    os.environ['TEMP'] = working_tmp
    os.environ['PYTHON_EGG_CACHE'] = working_tmp
    
    # Явно встановлюємо tempfile.tempdir
    tempfile.tempdir = working_tmp
else:
    print("EDXTMP: WARNING - No working tmp directory found!") 