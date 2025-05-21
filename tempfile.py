"""Super agresive patched temporary file handling routines"""

import os
import io
import re
import sys
import errno
import functools
import warnings
import weakref
import stat
import contextlib
from random import Random as _Random

try:
    import _thread
except ImportError:
    import _dummy_thread as _thread

_allocate_lock = _thread.allocate_lock

# Force our own version of _os.path.exists() to be used inside the original tempfile
_os = os

print("EDXTMP: SUPER AGGRESSIVE Monkeypatching tempfile")

# Список всіх можливих тимчасових директорій
_candidate_tempdir_list = [
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
    os.path.join(os.path.expanduser('~'), 'tmp'),
    '/.tmp',
    '/app/.tmp',
]

# Створюємо всі директорії
for dir_path in _candidate_tempdir_list:
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, mode=0o1777, exist_ok=True)
        
        # Встановлюємо максимальні права доступу
        try:
            os.chmod(dir_path, 0o1777)  # 1777 - sticky bit
        except Exception:
            try:
                os.chmod(dir_path, 0o777)  # якщо не можемо встановити sticky bit
            except Exception:
                pass
        
        print(f"EDXTMP: Created/fixed {dir_path}")
    except Exception as ex:
        print(f"EDXTMP: Error creating {dir_path}: {ex}")

# Знаходимо першу робочу директорію
_working_dir = None
for dir_path in _candidate_tempdir_list:
    try:
        if os.path.isdir(dir_path):
            try:
                # Перевіряємо доступ на запис
                if not os.access(dir_path, os.W_OK):
                    continue
                
                # Додаткова перевірка через файл
                test_file = os.path.join(dir_path, f"test_write_permissions_{os.getpid()}")
                with open(test_file, 'w') as f:
                    f.write('test')
                os.unlink(test_file)
                
                _working_dir = dir_path
                print(f"EDXTMP: Using {_working_dir} as tempdir")
                break
            except Exception as ex:
                print(f"EDXTMP: Cannot use {dir_path}: {ex}")
    except Exception as ex:
        print(f"EDXTMP: Cannot access {dir_path}: {ex}")
        continue

# Якщо не знайшли робочу директорію, створюємо свою в поточній директорії
if not _working_dir:
    try:
        try:
            cwd = os.getcwd()
        except Exception:
            cwd = '.'
        
        fallback_dir = os.path.join(cwd, '.tmp_fallback')
        os.makedirs(fallback_dir, mode=0o777, exist_ok=True)
        
        try:
            os.chmod(fallback_dir, 0o777)
        except Exception:
            pass
        
        test_file = os.path.join(fallback_dir, "test_write")
        with open(test_file, 'w') as f:
            f.write('test')
        os.unlink(test_file)
        
        _working_dir = fallback_dir
        print(f"EDXTMP: Using fallback directory: {_working_dir}")
    except Exception as ex:
        print(f"EDXTMP: Failed to create fallback dir: {ex}")
        # Last resort - try current directory
        _working_dir = '.'
        print("EDXTMP: WARNING - Using current directory as last resort")

# Якщо ми знайшли робочу директорію, використовуємо її
if _working_dir:
    tempdir = _working_dir
    os.environ['TMPDIR'] = _working_dir
    os.environ['TMP'] = _working_dir
    os.environ['TEMP'] = _working_dir
    os.environ['PYTHON_EGG_CACHE'] = _working_dir
else:
    print("EDXTMP: WARNING: No working temporary directory found, using /tmp anyway")
    tempdir = '/tmp'  # Вказуємо /tmp, навіть якщо це не працює

# Перевизначаємо функцію gettempdir
def gettempdir():
    """Our patched version of gettempdir that returns our pre-created tempdir."""
    return tempdir

# Перевизначаємо функцію mkstemp для підтримки помилкових параметрів
def mkstemp(suffix=None, prefix=None, dir=None, text=False):
    """Patched mkstemp that always uses our tempdir."""
    import tempfile as _tempfile
    
    # Ігноруємо параметр dir і завжди використовуємо наш tempdir
    return _tempfile._mkstemp_inner(suffix, prefix, tempdir, text)

# Перевизначаємо функцію mkdtemp для підтримки помилкових параметрів
def mkdtemp(suffix=None, prefix=None, dir=None):
    """Patched mkdtemp that always uses our tempdir."""
    import tempfile as _tempfile
    
    # Ігноруємо параметр dir і завжди використовуємо наш tempdir
    return _tempfile._mkdtemp_inner(suffix, prefix, tempdir)

# І gettempprefix для підтримки бібліотеки tempfile
def gettempprefix():
    """Our patched version of gettempprefix."""
    return 'tmp'

# Тестуємо наші функції
try:
    fd, path = mkstemp()
    print(f"EDXTMP: Test mkstemp successful: {path}")
    os.close(fd)
    os.unlink(path)
except Exception as ex:
    print(f"EDXTMP: Test mkstemp failed: {ex}")

try:
    path = mkdtemp()
    print(f"EDXTMP: Test mkdtemp successful: {path}")
    os.rmdir(path)
except Exception as ex:
    print(f"EDXTMP: Test mkdtemp failed: {ex}")

# Для уникнення помилок з циклічними імпортами
__all__ = ['tempdir', 'gettempdir', 'gettempprefix', 'mkstemp', 'mkdtemp']

# Реекспортуємо інші символи з оригінального tempfile
if 'tempfile' in sys.modules:
    _orig_tempfile = sys.modules['tempfile']
    for attr in dir(_orig_tempfile):
        if not attr.startswith('_') and attr not in globals():
            globals()[attr] = getattr(_orig_tempfile, attr) 