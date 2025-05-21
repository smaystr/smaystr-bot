package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"

	"github.com/smaystr/smaystr-bot/cmd"
)

// init створює всі можливі тимчасові директорії
func init() {
	// Список всіх можливих тимчасових директорій
	tempDirs := []string{
		"/tmp",
		"/var/tmp",
		"/usr/tmp",
		"/edx/app/xqwatcher/src/tmp",
		"/edx/app/xqwatcher/src",
		filepath.Join(os.TempDir(), "tmp"),
	}

	// Створюємо всі директорії та встановлюємо права
	for _, dir := range tempDirs {
		err := os.MkdirAll(dir, 0777)
		if err != nil {
			fmt.Printf("Помилка створення %s: %v\n", dir, err)
			continue
		}

		// Перевіряємо, чи можемо писати
		testFile := filepath.Join(dir, "test-write")
		err = ioutil.WriteFile(testFile, []byte("test"), 0666)
		if err == nil {
			os.Remove(testFile) // видаляємо тестовий файл, якщо вдалося записати
			fmt.Printf("Успішно створено та перевірено директорію: %s\n", dir)
		} else {
			fmt.Printf("Не вдалося записати в %s: %v\n", dir, err)
		}
	}
}

func main() {
	cmd.Execute()
}
