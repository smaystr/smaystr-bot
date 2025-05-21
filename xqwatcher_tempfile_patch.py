#!/usr/bin/env python3
"""
xqwatcher_tempfile_patch.py - Агресивний патч для Python tempfile.
Замінює стандартний модуль tempfile повністю власною реалізацією.

ІНСТРУКЦІЯ З ВИКОРИСТАННЯ:
1. Додайте цей файл в кореневу директорію вашого проекту
2. На початку вашого головного файлу додайте:
   import xqwatcher_tempfile_patch
   
   АБО
   
3. Запустіть ваш код через:
   PYTHONPATH=/path/to/this/file python -c "import xqwatcher_tempfile_patch; import your_module"
"""

import os
import sys
import random
import string
import io
import stat
import warnings
import atexit

# Спочатку зберігаємо оригінальний tempfile, щоб пізніше його замінити
import tempfile as original_tempfile
original_gettempdir = original_tempfile.gettempdir
original_mkstemp = original_tempfile.mkstemp
original_mkdtemp = original_tempfile.mkdtemp

# Список можливих тимчасових директорій в порядку пріоритету
_CANDIDATE_TEMPDIRS = [
    os.getcwd(),
    os.path.join(os.getcwd(), 'tmp'),
    os.path.join(os.getcwd(), '.tmp'),
    '/edx/app/xqwatcher/src',
    '/edx/app/xqwatcher/src/tmp',
    '/tmp',
    '/var/tmp',
    '/usr/tmp',
]

# Оголошуємо глобальні змінні
_tempdir = None
_created_directories = []

def _create_directory(dir_path):
    """Створює директорію з правами 0777 і перевіряє права на запис."""
    try:
        os.makedirs(dir_path, exist_ok=True)
        os.chmod(dir_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        print(f"Створено директорію: {dir_path}")
        return True
    except Exception as e:
        print(f"Помилка створення директорії {dir_path}: {e}")
        return False

def _is_dir_writable(dir_path):
    """Перевіряє чи директорія існує і чи є права на запис."""
    if not os.path.isdir(dir_path):
        return False
    
    # Спробуємо створити тестовий файл
    test_file = os.path.join(dir_path, f".test_write_{os.getpid()}_{random.randint(1000, 9999)}")
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.unlink(test_file)
        return True
    except Exception:
        return False

def _initialize_tempdir():
    """Ініціалізує глобальну змінну _tempdir."""
    global _tempdir
    
    # Перебираємо всі можливі директорії
    for dir_path in _CANDIDATE_TEMPDIRS:
        # Спробуємо створити директорію, якщо її немає
        if not os.path.exists(dir_path):
            if not _create_directory(dir_path):
                continue
            _created_directories.append(dir_path)
        
        # Перевіряємо чи є права на запис
        if _is_dir_writable(dir_path):
            _tempdir = dir_path
            print(f"Використовую тимчасову директорію: {_tempdir}")
            
            # Встановлюємо також змінні середовища
            os.environ['TMPDIR'] = _tempdir
            os.environ['TEMP'] = _tempdir
            os.environ['TMP'] = _tempdir
            return
    
    # Якщо не знайшли жодної директорії - створюємо в поточній
    fallback_dir = os.path.join(os.getcwd(), '.xqtmp')
    if _create_directory(fallback_dir):
        _tempdir = fallback_dir
        _created_directories.append(fallback_dir)
        os.environ['TMPDIR'] = _tempdir
        os.environ['TEMP'] = _tempdir
        os.environ['TMP'] = _tempdir
        print(f"Використовую fallback директорію: {_tempdir}")
    else:
        raise RuntimeError("Не вдалося знайти або створити жодної тимчасової директорії!")

def _cleanup_temp_directories():
    """Видаляє тимчасові директорії при завершенні роботи."""
    for dir_path in _created_directories:
        try:
            import shutil
            shutil.rmtree(dir_path, ignore_errors=True)
            print(f"Видалено тимчасову директорію: {dir_path}")
        except Exception as e:
            print(f"Помилка видалення {dir_path}: {e}")

# Ініціалізація при імпорті
_initialize_tempdir()
atexit.register(_cleanup_temp_directories)

# Нові реалізації функцій модуля tempfile

def gettempdir():
    """Повертає шлях до тимчасової директорії."""
    global _tempdir
    if _tempdir is None:
        _initialize_tempdir()
    return _tempdir

def gettempdirb():
    """Повертає шлях до тимчасової директорії як bytes."""
    return gettempdir().encode(sys.getfilesystemencoding())

def mkstemp(suffix=None, prefix=None, dir=None, text=False):
    """Створює тимчасовий файл."""
    if dir is None:
        dir = gettempdir()
    
    if not os.path.isdir(dir):
        _create_directory(dir)
    
    if suffix is None:
        suffix = ""
    if prefix is None:
        prefix = "tmp"
    
    # Генеруємо унікальне ім'я файлу
    chars = string.ascii_letters + string.digits
    name = prefix + ''.join(random.choice(chars) for _ in range(8)) + suffix
    path = os.path.join(dir, name)
    
    # Створюємо файл
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
    if not text and hasattr(os, 'O_BINARY'):
        flags |= os.O_BINARY
    
    fd = os.open(path, flags, 0o600)
    return fd, path

def mkdtemp(suffix=None, prefix=None, dir=None):
    """Створює тимчасову директорію."""
    if dir is None:
        dir = gettempdir()
    
    if not os.path.isdir(dir):
        _create_directory(dir)
    
    if suffix is None:
        suffix = ""
    if prefix is None:
        prefix = "tmp"
    
    # Генеруємо унікальне ім'я директорії
    chars = string.ascii_letters + string.digits
    name = prefix + ''.join(random.choice(chars) for _ in range(8)) + suffix
    path = os.path.join(dir, name)
    
    # Створюємо директорію
    os.mkdir(path, 0o700)
    return path

def TemporaryFile(mode='w+b', buffering=-1, encoding=None, newline=None, 
                 suffix=None, prefix=None, dir=None):
    """Повертає тимчасовий файловий об'єкт."""
    fd, path = mkstemp(suffix=suffix, prefix=prefix, dir=dir)
    try:
        os.unlink(path)
        return os.fdopen(fd, mode, buffering, encoding, newline)
    except:
        os.close(fd)
        raise

# Патчимо оригінальний модуль tempfile
import sys
sys.modules['tempfile'].gettempdir = gettempdir
sys.modules['tempfile'].gettempdirb = gettempdirb
sys.modules['tempfile'].mkstemp = mkstemp
sys.modules['tempfile'].mkdtemp = mkdtemp
sys.modules['tempfile'].TemporaryFile = TemporaryFile
sys.modules['tempfile'].tempdir = gettempdir()

# Виводимо діагностичну інформацію
print(f"XQWatcher tempfile patch застосовано!")
print(f"Поточна тимчасова директорія: {gettempdir()}")
print(f"Змінні середовища: TMPDIR={os.environ.get('TMPDIR', '<не встановлено>')}")

# Тестуємо, що все працює
try:
    fd, path = mkstemp()
    print(f"Тест створення файлу: {path}")
    os.close(fd)
    os.unlink(path)
    
    test_dir = mkdtemp()
    print(f"Тест створення директорії: {test_dir}")
    os.rmdir(test_dir)
    
    print("Тест успішний!")
except Exception as e:
    print(f"Помилка тесту: {e}") 