#!/usr/bin/env python3
# Просто вставте цей код на початку вашого основного файлу перед імпортом інших модулів

import os
import sys
import tempfile

# Створюємо гарантовано робочу тимчасову директорію прямо в поточній
CWD = os.getcwd()
FORCED_TMP = os.path.join(CWD, '.forced_tmp')

try:
    # Створюємо директорію, якщо не існує
    if not os.path.exists(FORCED_TMP):
        os.makedirs(FORCED_TMP, mode=0o777)
    
    # Встановлюємо як тимчасову директорію
    os.environ['TMPDIR'] = FORCED_TMP
    os.environ['TMP'] = FORCED_TMP
    os.environ['TEMP'] = FORCED_TMP
    
    # Патчимо tempfile напряму
    tempfile.tempdir = FORCED_TMP
    
    # Тестуємо що все працює
    test_fd, test_path = tempfile.mkstemp(prefix='test_')
    os.close(test_fd)
    os.unlink(test_path)
    print(f"TEMP FIX: Успішно налаштовано тимчасову директорію: {FORCED_TMP}")
except Exception as e:
    # Якщо щось пішло не так, створюємо прямо у поточній директорії
    print(f"TEMP FIX: Помилка: {e}")
    try:
        FORCED_TMP = CWD
        os.environ['TMPDIR'] = FORCED_TMP
        os.environ['TMP'] = FORCED_TMP
        os.environ['TEMP'] = FORCED_TMP
        tempfile.tempdir = FORCED_TMP
        print(f"TEMP FIX: Використовую поточну директорію як тимчасову: {FORCED_TMP}")
    except Exception as e2:
        print(f"TEMP FIX: Критична помилка: {e2}") 