#!/usr/bin/env python3
"""
Скрипт для налаштування середовища для тестів GlobalLogic
Запускати перед тестами: python setup_env.py
"""
import os
import sys
import stat
import tempfile

print("========== НАЛАШТУВАННЯ ТИМЧАСОВИХ ДИРЕКТОРІЙ ==========")

# Зберегти оригінальний tempfile.gettempdir
original_gettempdir = tempfile.gettempdir

# Список всіх можливих тимчасових директорій
TEMP_DIRS = [
    '/tmp',
    '/var/tmp',
    '/usr/tmp',
    '/edx/app/xqwatcher/src/tmp',
    '/edx/app/xqwatcher/src',
    os.path.join(os.getcwd(), '.tmp'),
    os.path.join(os.getcwd(), 'tmp'),
]

# Функція для перевірки доступу на запис
def is_writable(dir_path):
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"Створено директорію: {dir_path}")
        except Exception as e:
            print(f"Не вдалося створити {dir_path}: {e}")
            return False
    
    # Спробувати встановити права 0777
    try:
        os.chmod(dir_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        print(f"Встановлено права 0777 для {dir_path}")
    except Exception as e:
        print(f"Не вдалося змінити права для {dir_path}: {e}")
    
    # Перевірити можливість запису
    test_file = os.path.join(dir_path, f"test_write_{os.getpid()}")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.unlink(test_file)
        print(f"Директорія доступна для запису: {dir_path}")
        return True
    except Exception as e:
        print(f"Не вдалося записати в {dir_path}: {e}")
        return False

# Знайти першу доступну для запису директорію
writable_dirs = []
for temp_dir in TEMP_DIRS:
    if is_writable(temp_dir):
        writable_dirs.append(temp_dir)

if writable_dirs:
    print(f"Знайдено {len(writable_dirs)} директорій, доступних для запису:")
    for dir_path in writable_dirs:
        print(f"  - {dir_path}")
    
    # Встановити першу доступну директорію як TMPDIR
    os.environ['TMPDIR'] = writable_dirs[0]
    os.environ['TMP'] = writable_dirs[0]
    os.environ['TEMP'] = writable_dirs[0]
    print(f"Встановлено TMPDIR={writable_dirs[0]}")
    
    # Переопределить функцию gettempdir
    def patched_gettempdir():
        for d in writable_dirs:
            return d
        return original_gettempdir()
    
    tempfile.gettempdir = patched_gettempdir
    print(f"tempfile.gettempdir() = {tempfile.gettempdir()}")
else:
    print("ПОМИЛКА: Не знайдено жодної директорії, доступної для запису")

# Вивести інформацію про поточне середовище
print("\n========== ІНФОРМАЦІЯ ПРО СИСТЕМУ ==========")
print(f"Python: {sys.version}")
print(f"Платформа: {sys.platform}")
print(f"Поточна директорія: {os.getcwd()}")
print(f"Змінні середовища:")
print(f"  TMPDIR={os.environ.get('TMPDIR', '<не встановлено>')}")
print(f"  TMP={os.environ.get('TMP', '<не встановлено>')}")
print(f"  TEMP={os.environ.get('TEMP', '<не встановлено>')}")
print(f"tempfile.gettempdir() = {tempfile.gettempdir()}")

print("\n========== ПЕРЕВІРКА ДОСТУПУ ДО ТИМЧАСОВИХ ФАЙЛІВ ==========")
try:
    temp_fd, temp_path = tempfile.mkstemp()
    os.write(temp_fd, b"test")
    os.close(temp_fd)
    print(f"Успішно створено тимчасовий файл: {temp_path}")
    os.unlink(temp_path)
    print("Тимчасовий файл успішно видалено")
except Exception as e:
    print(f"ПОМИЛКА при створенні тимчасового файлу: {e}")

print("\n========== НАЛАШТУВАННЯ ЗАВЕРШЕНО ==========") 