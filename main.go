package main

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/smaystr/smaystr-bot/cmd"
)

func init() {
	// Attempt to create tmp directories before any other code executes
	fmt.Println("Creating temporary directories...")

	// Перевіряємо чи існують каталоги, не намагаємося змінювати права

	// Визначаємо можливі tmp каталоги в порядку пріоритету
	tmpDirs := []string{
		"/tmp",                     // Стандартний Linux tmp
		"/var/tmp",                 // Альтернативний Linux tmp
		"/usr/tmp",                 // Ще один варіант
		filepath.Join(".", ".tmp"), // Локальний .tmp в поточній директорії
		filepath.Join(".", "tmp"),  // Локальний tmp
	}

	// Функція для перевірки чи каталог існує і чи є права на запис
	checkTmpDir := func(dir string) bool {
		// Перевіряємо існування
		info, err := os.Stat(dir)
		if os.IsNotExist(err) {
			return false
		}
		if err != nil {
			fmt.Printf("Error checking %s: %v\n", dir, err)
			return false
		}

		// Перевіряємо, чи це директорія
		if !info.IsDir() {
			return false
		}

		// Перевіряємо права на запис створивши тимчасовий файл
		testPath := filepath.Join(dir, fmt.Sprintf("test-%d", os.Getpid()))
		f, err := os.Create(testPath)
		if err != nil {
			fmt.Printf("%s is not writable: %v\n", dir, err)
			return false
		}
		f.Close()
		os.Remove(testPath)

		fmt.Printf("Found usable tmp directory: %s\n", dir)
		return true
	}

	// Перевіряємо кожен каталог
	for _, dir := range tmpDirs {
		if checkTmpDir(dir) {
			// Знайшли робочий каталог, встановлюємо змінні середовища
			os.Setenv("TMPDIR", dir)
			os.Setenv("TMP", dir)
			os.Setenv("TEMP", dir)
			fmt.Printf("Set TMPDIR=%s\n", dir)
			// Знайшли робочий каталог, виходимо з циклу
			return
		}
	}

	// Якщо дійшли досюди, спробуємо створити хоча б один каталог

	// Try multiple possible tmp directories
	tmpDirs = []string{
		filepath.Join(".", ".tmp"),
		filepath.Join(".", "tmp"),
		"/tmp",
		"/var/tmp",
		"/usr/tmp",
		"/edx/app/xqwatcher/src/tmp",
	}

	for _, dir := range tmpDirs {
		err := os.MkdirAll(dir, 0777)
		if err != nil {
			// Просто логуємо помилку і продовжуємо
			fmt.Printf("Could not create %s: %v\n", dir, err)
			continue
		} else {
			fmt.Printf("Created %s directory\n", dir)
			os.Setenv("TMPDIR", dir)
			os.Setenv("TMP", dir)
			os.Setenv("TEMP", dir)
			fmt.Printf("Set TMPDIR=%s\n", dir)
			return
		}
	}

	fmt.Println("WARNING: Could not find or create any usable temp directory")
	fmt.Println("Application may fail if it needs to write temporary files")
}

func main() {
	cmd.Execute()
}
