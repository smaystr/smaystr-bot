"""Patched temporary file handling routines"""

import os
import io
import re
import sys
import errno
import functools
import warnings
import weakref
import contextlib
from random import Random as _Random

try:
    import _thread
except ImportError:
    import _dummy_thread as _thread

_allocate_lock = _thread.allocate_lock

# Force our own version of _os.path.exists() to be used inside the original tempfile
_os = os

print("EDXTMP: Monkeypatching tempfile")

# Список всіх можливих тимчасових директорій
_candidate_tempdir_list = [
    '/tmp',
    '/var/tmp',
    '/usr/tmp',
    '/edx/app/xqwatcher/src',
    os.path.join(os.getcwd(), '.tmp'),
    os.path.join(os.getcwd(), 'tmp')
]

# Створюємо всі директорії
for dir_path in _candidate_tempdir_list:
    try:
        os.makedirs(dir_path, mode=0o1777, exist_ok=True)
        os.chmod(dir_path, 0o1777)  # 1777 - sticky bit
        print(f"EDXTMP: Created/fixed {dir_path}")
    except Exception as ex:
        print(f"EDXTMP: Error creating {dir_path}: {ex}")

# Знаходимо першу робочу директорію
_working_dir = None
for dir_path in _candidate_tempdir_list:
    try:
        if os.path.isdir(dir_path) and os.access(dir_path, os.W_OK):
            test_file = os.path.join(dir_path, "test_write_permissions")
            with open(test_file, 'w') as f:
                f.write('test')
            os.unlink(test_file)
            _working_dir = dir_path
            print(f"EDXTMP: Using {_working_dir} as tempdir")
            break
    except Exception as ex:
        print(f"EDXTMP: Cannot use {dir_path}: {ex}")
        continue

# Якщо ми знайшли робочу директорію, використовуємо її
if _working_dir:
    tempdir = _working_dir
    os.environ['TMPDIR'] = _working_dir
    os.environ['TMP'] = _working_dir
    os.environ['TEMP'] = _working_dir
else:
    print("EDXTMP: WARNING: No working temporary directory found")
    tempdir = None

# Реекспортуємо оригінальний tempfile
if 'tempfile' in sys.modules:
    _orig_tempfile = sys.modules['tempfile']
    # Переміщаємо всі функції з оригіналу
    for attr in dir(_orig_tempfile):
        if not attr.startswith('_') and attr not in globals():
            globals()[attr] = getattr(_orig_tempfile, attr)

# Перевизначаємо функцію gettempdir
def gettempdir():
    """Our patched version of gettempdir that returns our pre-created tempdir."""
    if tempdir:
        return tempdir
    # Якщо у нас немає tempdir, повертаємо стандартне значення
    return os.path.normcase(os.path.abspath(
        os.environ.get('TMPDIR') or os.environ.get('TMP') or 
        os.environ.get('TEMP') or '/tmp'))

# І meetempprefix для підтримки бібліотеки tempfile
def gettempprefix():
    """Our patched version of gettempprefix."""
    return 'tmp'

# Для уникнення помилок з циклічними імпортами
__all__ = ['tempdir', 'gettempdir', 'gettempprefix'] 