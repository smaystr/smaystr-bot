// Entrypoint для Docker, який налаштує тимчасові директорії
package main

import (
	"fmt"
	"os"
	"path/filepath"
	"syscall"
)

func main() {
	fmt.Println("Налаштування тимчасових директорій в Docker...")

	// Створюємо всі можливі тимчасові директорії
	dirs := []string{
		"/tmp",
		"/var/tmp",
		"/usr/tmp",
		"/edx/app/xqwatcher/src/tmp",
	}

	for _, dir := range dirs {
		err := os.MkdirAll(dir, 0777)
		if err != nil {
			fmt.Printf("Помилка створення %s: %v\n", dir, err)
		} else {
			// Встановлюємо права 0777
			err = os.Chmod(dir, 0777)
			if err != nil {
				fmt.Printf("Помилка встановлення прав для %s: %v\n", dir, err)
			} else {
				fmt.Printf("Створено директорію з правами: %s\n", dir)
			}
		}
	}

	// Встановлюємо змінні середовища
	os.Setenv("TMPDIR", "/tmp")
	os.Setenv("TMP", "/tmp")
	os.Setenv("TEMP", "/tmp")
	os.Setenv("TEMPDIR", "/tmp")
	os.Setenv("PYTHON_EGG_CACHE", "/tmp")

	fmt.Println("Змінні середовища встановлено")

	// Перевіряємо, чи можна писати в тимчасову директорію
	testPath := filepath.Join("/tmp", "test_write")
	testFile, err := os.Create(testPath)
	if err != nil {
		fmt.Printf("Проблема з директорією /tmp: %v\n", err)
		fmt.Println("Використовую корінь контейнера")
		os.Setenv("TMPDIR", "/")
		os.Setenv("TMP", "/")
		os.Setenv("TEMP", "/")
	} else {
		testFile.Close()
		os.Remove(testPath)
		fmt.Println("Директорія /tmp доступна для запису")
	}

	// Запуск основної програми
	fmt.Println("Запуск основної програми...")

	// Перевіряємо, чи є аргументи
	if len(os.Args) < 2 {
		fmt.Println("Помилка: Не вказано шлях до основної програми")
		os.Exit(1)
	}

	// Отримуємо шлях до програми та аргументи
	program := os.Args[1]
	args := append([]string{program}, os.Args[2:]...)

	// Використовуємо syscall.Exec для повної заміни процесу
	// Це дозволяє правильно передати сигнали та вийти з процесу з правильним кодом
	err = syscall.Exec(program, args, os.Environ())
	if err != nil {
		fmt.Printf("Помилка запуску %s: %v\n", program, err)
		os.Exit(1)
	}
}
