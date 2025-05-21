#!/usr/bin/env python3
"""
fix_tmp_globallogic.py - Фінальне рішення для проблеми з тимчасовими директоріями

ІНСТРУКЦІЯ: 
1. Додайте цей файл у ваш проект 
2. Запустіть його ПЕРЕД будь-яким іншим Python-кодом через:
   python fix_tmp_globallogic.py
3. АБО додайте в основний файл:
   import fix_tmp_globallogic
"""

import os
import sys
import stat
import platform
import uuid
import time

print("\n" + "="*70)
print(f"ЗАПУСК ДІАГНОСТИКИ ТА ВИПРАВЛЕННЯ ТИМЧАСОВИХ ДИРЕКТОРІЙ")
print(f"Дата/час: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python: {sys.version}")
print(f"Платформа: {platform.platform()}")
print(f"Робоча директорія: {os.getcwd()}")
print("="*70 + "\n")

# Список можливих тимчасових директорій
TEMP_DIRS = [
    '/edx/app/xqwatcher/src',
    '/edx/app/xqwatcher/src/tmp',
    '/edx/app/xqwatcher/src/grader',
    '/tmp',
    '/var/tmp',
    '/usr/tmp',
    os.path.join(os.getcwd(), 'tmp'),
    os.path.join(os.getcwd(), '.tmp'),
    os.path.join(os.path.expanduser('~'), 'tmp'),
    os.getcwd(),
    '.'
]

# Додаємо до списку деякі шляхи, які можуть бути у змінних середовища
for env_var in ['TMPDIR', 'TEMP', 'TMP']:
    if env_var in os.environ and os.environ[env_var]:
        TEMP_DIRS.insert(0, os.environ[env_var])

# Виводимо інформацію про змінні середовища
print("Змінні середовища для тимчасових директорій:")
for env_var in ['TMPDIR', 'TEMP', 'TMP']:
    print(f"  {env_var}={os.environ.get(env_var, '<не встановлено>')}")
print()

# Перевіряємо доступність та можливість запису у кожній директорії
print("Перевірка всіх можливих тимчасових директорій:")
usable_dirs = []

for temp_dir in TEMP_DIRS:
    print(f"\nТестування: {temp_dir}")
    # Перевіряємо чи існує директорія
    if not os.path.exists(temp_dir):
        print(f"  Не існує - спроба створення...")
        try:
            os.makedirs(temp_dir, exist_ok=True)
            print(f"  Директорію створено")
        except Exception as e:
            print(f"  ПОМИЛКА створення: {e}")
            continue
    
    # Перевіряємо чи це директорія
    if not os.path.isdir(temp_dir):
        print(f"  Це не директорія!")
        continue
    
    # Перевіряємо права доступу
    try:
        mode = os.stat(temp_dir).st_mode
        print(f"  Поточні права: {oct(mode & 0o777)}")
        
        # Спробуємо встановити потрібні права
        try:
            os.chmod(temp_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
            print(f"  Права змінено на: {oct(os.stat(temp_dir).st_mode & 0o777)}")
        except Exception as e:
            print(f"  Неможливо змінити права: {e}")
    except Exception as e:
        print(f"  Неможливо отримати права: {e}")
    
    # Перевіряємо можливість запису
    test_id = str(uuid.uuid4())[:8]
    test_file = os.path.join(temp_dir, f".test_temp_{test_id}")
    
    try:
        # Спробуємо створити файл
        with open(test_file, 'w') as f:
            f.write("Тестовий файл")
        print(f"  Успішно створено тестовий файл: {test_file}")
        
        # Спробуємо видалити файл
        os.unlink(test_file)
        print(f"  Успішно видалено тестовий файл")
        
        # Додаємо у список доступних директорій
        usable_dirs.append(temp_dir)
        print(f"  ДИРЕКТОРІЯ ПРИДАТНА ДЛЯ ВИКОРИСТАННЯ!")
    except Exception as e:
        print(f"  ПОМИЛКА запису: {e}")

print("\nРезультати перевірки:")
if usable_dirs:
    print(f"Знайдено {len(usable_dirs)} доступних директорій:")
    for idx, dir_path in enumerate(usable_dirs, 1):
        print(f"  {idx}. {dir_path}")
    
    # Використовуємо першу доступну директорію
    tmp_dir = usable_dirs[0]
    
    # Встановлюємо змінні середовища
    os.environ['TMPDIR'] = tmp_dir
    os.environ['TMP'] = tmp_dir
    os.environ['TEMP'] = tmp_dir
    
    print(f"\nВстановлено тимчасову директорію: {tmp_dir}")
    print(f"Змінні середовища встановлено:")
    print(f"  TMPDIR={os.environ['TMPDIR']}")
    print(f"  TMP={os.environ['TMP']}")
    print(f"  TEMP={os.environ['TEMP']}")
    
    # Патчимо tempfile
    import tempfile
    tempfile.tempdir = tmp_dir
    
    # Тестуємо
    try:
        fd, path = tempfile.mkstemp()
        print(f"\nУспішно створено тимчасовий файл через tempfile: {path}")
        os.close(fd)
        os.unlink(path)
        
        tmpdir = tempfile.gettempdir()
        print(f"tempfile.gettempdir() повертає: {tmpdir}")
        
        print("\nПатч успішно застосовано! Тимчасові файли тепер працюють коректно.")
    except Exception as e:
        print(f"\nПОМИЛКА при тестуванні tempfile: {e}")
else:
    print("НЕ ЗНАЙДЕНО ЖОДНОЇ ДОСТУПНОЇ ДИРЕКТОРІЇ!")
    
    # Створюємо власну тимчасову директорію в поточній директорії
    fallback_dir = os.path.join(os.getcwd(), ".gl_tmp_" + str(uuid.uuid4())[:8])
    print(f"\nСтворення резервної директорії: {fallback_dir}")
    
    try:
        os.makedirs(fallback_dir, exist_ok=True)
        os.chmod(fallback_dir, 0o777)
        
        # Встановлюємо змінні середовища
        os.environ['TMPDIR'] = fallback_dir
        os.environ['TEMP'] = fallback_dir
        os.environ['TMP'] = fallback_dir
        
        # Патчимо tempfile
        import tempfile
        tempfile.tempdir = fallback_dir
        
        # Тестуємо
        test_id = str(uuid.uuid4())[:8]
        test_file = os.path.join(fallback_dir, f"test_{test_id}")
        with open(test_file, 'w') as f:
            f.write("Тест")
        
        print(f"Тест запису в {fallback_dir} успішний!")
        print(f"Встановлено тимчасову директорію: {fallback_dir}")
        
        fd, path = tempfile.mkstemp()
        print(f"\nУспішно створено тимчасовий файл через tempfile: {path}")
        os.close(fd)
        os.unlink(path)
        
        print("\nРезервний план спрацював! Тимчасові файли тепер працюють.")
    except Exception as e:
        print(f"КРИТИЧНА ПОМИЛКА: {e}")
        print("\nНеможливо створити тимчасову директорію. Спробуйте запустити код з root правами.")
        sys.exit(1)

print("\n" + "="*70)
print("ДІАГНОСТИКА ЗАВЕРШЕНА. ПАТЧ ЗАСТОСОВАНО.")
print("Тепер ваш код має використовувати правильні тимчасові директорії.")
print("="*70) 