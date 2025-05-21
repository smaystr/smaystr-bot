#!/usr/bin/env python3

# === ПОЧАТОК ХАКУ ДЛЯ ТИМЧАСОВИХ ДИРЕКТОРІЙ ===
import os, sys
_local_tmp = os.path.abspath(os.path.join(os.getcwd(), '.hwtmp'))
try:
    # Створюємо директорію
    os.makedirs(_local_tmp, exist_ok=True)
    
    # Перевіряємо права на запис
    _test_file = os.path.join(_local_tmp, 'test_write')
    with open(_test_file, 'w') as f:
        f.write('test')
    os.unlink(_test_file)
    
    # Встановлюємо змінні середовища
    os.environ['TMPDIR'] = _local_tmp
    os.environ['TEMP'] = _local_tmp
    os.environ['TMP'] = _local_tmp
    
    # Спочатку імпортуємо tempfile і зберігаємо оригінальний gettempdir
    import tempfile
    _orig_tempdir = tempfile.gettempdir
    
    # Прямо перевизначаємо tempfile.tempdir
    tempfile.tempdir = _local_tmp
    
    # Перевизначаємо tempfile.gettempdir
    def _fixed_gettempdir():
        return _local_tmp
    
    tempfile.gettempdir = _fixed_gettempdir
    
    # Тестуємо
    _tmp_fd, _tmp_path = tempfile.mkstemp()
    os.close(_tmp_fd)
    os.unlink(_tmp_path)
    print(f"SUCCESS: temporary directory fixed: {_local_tmp}")
except Exception as e:
    print(f"WARNING: temporary directory hack failed: {e}")
# === КІНЕЦЬ ХАКУ ДЛЯ ТИМЧАСОВИХ ДИРЕКТОРІЙ ===

# === ТЕПЕР ВАШ ЗВИЧАЙНИЙ КОД ===
# Приклад використання tempfile
import tempfile
print(f"Current temp dir: {tempfile.gettempdir()}")
fd, path = tempfile.mkstemp()
print(f"Created temp file: {path}")
os.close(fd)
os.unlink(path)
print("Temp file test successful!") 