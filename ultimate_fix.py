#!/usr/bin/env python3
"""
АБСОЛЮТНО ОСТАННЄ РІШЕННЯ ДЛЯ ПРОБЛЕМИ З ТИМЧАСОВИМИ ДИРЕКТОРІЯМИ

ВИКОРИСТАННЯ:
1. Запустіть ваш скрипт через:
   python ultimate_fix.py ваш_скрипт.py аргумент1 аргумент2
   
2. АБО виконайте перед запуском:
   PYTHONPATH=. python -c "import ultimate_fix; ultimate_fix.install()" && python ваш_скрипт.py
"""

import os
import sys
import shutil
import builtins
import importlib.util
import types

# Гарантуємо наявність тимчасової директорії в поточній директорії
CURRENT_DIR = os.getcwd()
CUSTOM_TMP = os.path.join(CURRENT_DIR, '.ultratmp')

# Створюємо директорію з максимальними правами
try:
    os.makedirs(CUSTOM_TMP, mode=0o777, exist_ok=True)
    print(f"✅ Створено тимчасову директорію: {CUSTOM_TMP}")
except Exception as e:
    print(f"❌ Помилка створення директорії: {e}")
    # Спробуємо альтернативну директорію
    CUSTOM_TMP = os.path.join(CURRENT_DIR, 'tmp')
    try:
        os.makedirs(CUSTOM_TMP, mode=0o777, exist_ok=True)
        print(f"✅ Створено альтернативну директорію: {CUSTOM_TMP}")
    except Exception as e:
        print(f"❌ Помилка створення альтернативної директорії: {e}")
        CUSTOM_TMP = CURRENT_DIR
        print(f"⚠️ Використовую поточну директорію: {CUSTOM_TMP}")

# Встановлюємо всі можливі змінні середовища
os.environ['TMPDIR'] = CUSTOM_TMP
os.environ['TEMP'] = CUSTOM_TMP 
os.environ['TMP'] = CUSTOM_TMP
os.environ['TEMPDIR'] = CUSTOM_TMP
os.environ['PYTHON_EGG_CACHE'] = CUSTOM_TMP

print("✅ Встановлено змінні середовища")

# Перевіряємо чи можна записувати у директорію
test_path = os.path.join(CUSTOM_TMP, f'test_write_{os.getpid()}')
try:
    with open(test_path, 'w') as f:
        f.write('test')
    os.remove(test_path)
    print(f"✅ Тимчасова директорія доступна для запису: {CUSTOM_TMP}")
except Exception as e:
    print(f"❌ КРИТИЧНА ПОМИЛКА: Не можна записати у {CUSTOM_TMP}: {e}")
    sys.exit(1)

# Функція для оригінального імпорту
original_import = builtins.__import__

# Модифікація tempfile
_patched_tempfile = None

def _create_patched_tempfile():
    """Створює модифіковану версію модуля tempfile"""
    # Спочатку завантажуємо оригінальний модуль
    spec = importlib.util.find_spec('tempfile')
    if not spec:
        print("❌ Не можу знайти модуль tempfile")
        return None
    
    # Створюємо новий модуль
    patched = types.ModuleType('tempfile')
    
    # Завантажуємо оригінальний модуль
    original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    
    # Копіюємо всі атрибути
    for name in dir(original):
        if not name.startswith('__'):
            setattr(patched, name, getattr(original, name))
    
    # Встановлюємо основну директорію
    patched.tempdir = CUSTOM_TMP
    
    # Перевизначаємо ключові функції
    def patched_gettempdir():
        return CUSTOM_TMP
    
    def patched_mkstemp(suffix=None, prefix=None, dir=None, text=False):
        if dir is None:
            dir = CUSTOM_TMP
        return original.mkstemp(suffix=suffix, prefix=prefix, dir=dir, text=text)
    
    def patched_mkdtemp(suffix=None, prefix=None, dir=None):
        if dir is None:
            dir = CUSTOM_TMP
        return original.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    
    # Замінюємо функції
    patched.gettempdir = patched_gettempdir
    patched.mkstemp = patched_mkstemp
    patched.mkdtemp = patched_mkdtemp
    
    return patched

# Перехоплюємо імпорт tempfile
def patched_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == 'tempfile':
        global _patched_tempfile
        if _patched_tempfile is None:
            _patched_tempfile = _create_patched_tempfile()
        if _patched_tempfile:
            return _patched_tempfile
    
    # Продовжуємо стандартний імпорт
    return original_import(name, globals, locals, fromlist, level)

# Встановлюємо перехоплювач імпорту
builtins.__import__ = patched_import
print("✅ Встановлено перехоплювач імпорту для tempfile")

# Функція для випадку, якщо tempfile вже був імпортований
def patch_tempfile_directly():
    """Патчить модуль tempfile, якщо він вже був імпортований"""
    if 'tempfile' in sys.modules:
        tempfile = sys.modules['tempfile']
        tempfile.tempdir = CUSTOM_TMP
        
        # Якщо оригінальний метод був збережений - відновлюємо його
        if hasattr(tempfile, '_original_gettempdir'):
            tempfile.gettempdir = tempfile._original_gettempdir
        else:
            # Зберігаємо оригінальний метод
            tempfile._original_gettempdir = tempfile.gettempdir
        
        # Перезаписуємо метод
        def new_gettempdir():
            return CUSTOM_TMP
        
        tempfile.gettempdir = new_gettempdir
        print("✅ Застосовано патч до вже імпортованого модуля tempfile")

# Застосовуємо прямий патч
patch_tempfile_directly()

def install():
    """Функція для встановлення патчу"""
    print("✅ Патч для тимчасових директорій встановлено")

# Якщо запущено як основний скрипт
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Використання: {sys.argv[0]} <ваш_скрипт.py> [аргументи...]")
        sys.exit(1)
    
    # Запуск вказаного скрипта
    script_path = sys.argv[1]
    script_args = sys.argv[1:]
    
    print(f"🚀 Запуск скрипта {script_path} з ультимативним патчем tempfile...")
    
    # Збережемо шлях до скрипта для Python
    sys.argv = script_args
    
    # Завантаження і виконання скрипта
    try:
        with open(script_path, 'r') as f:
            script_code = f.read()
        
        # Виконуємо з глобальними змінними __main__
        exec(script_code, {'__name__': '__main__', '__file__': script_path})
    except Exception as e:
        print(f"❌ Помилка виконання скрипта {script_path}: {e}")
        sys.exit(1) 