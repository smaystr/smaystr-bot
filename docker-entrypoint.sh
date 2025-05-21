#!/bin/sh
set -e

echo "Налаштування тимчасових директорій в Docker..."

# Створюємо всі можливі тимчасові директорії
mkdir -p /tmp /var/tmp /usr/tmp /edx/app/xqwatcher/src/tmp
chmod -R 1777 /tmp /var/tmp /usr/tmp /edx/app/xqwatcher/src/tmp

# Встановлюємо змінні середовища
export TMPDIR=/tmp
export TMP=/tmp
export TEMP=/tmp
export TEMPDIR=/tmp
export PYTHON_EGG_CACHE=/tmp

# Перевіряємо, чи можна писати в тимчасову директорію
if touch /tmp/test_write && rm /tmp/test_write; then
    echo "✅ Директорія /tmp доступна для запису"
else
    echo "⚠️ Проблема з директорією /tmp. Використовую корінь контейнера"
    export TMPDIR=/
    export TMP=/
    export TEMP=/
fi

echo "Запуск основної програми..."
exec "$@" 