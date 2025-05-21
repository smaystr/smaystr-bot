# smaystr-bot

A tiny Telegram bot written in Go.  
It is primarily a playground for experimenting with the [telebot](https://github.com/tucnak/telebot) library, good engineering practises (clean project layout, CI/linting, tests) and modern tooling (`cobra`, `logrus`, Go modules).

> Live instance: **[@smaystr_bot](https://t.me/smaystr_bot)**

---

## Features

* `/start` – friendly greeting ⚡️
* `/ping`  – quick liveness check → replies `pong`
* Graceful shutdown on <kbd>Ctrl-C</kbd>
* Structured logging via **logrus**
* Table-driven unit tests with **testify** & coverage for CLI too

## Requirements

* Go ≥ 1.22
* A Telegram bot token – obtain via [@BotFather](https://t.me/BotFather)

## Quick Start

```bash
# 1. clone & enter
$ git clone https://github.com/smaystr/smaystr-bot.git && cd smaystr-bot

# 2. install deps
$ go mod download

# 3. create .env from template and add your token
$ cp env.example .env         # один раз
$ echo 'TELE_TOKEN=123456:ABC-DEF…' >> .env

# 4. run
$ go run .            # bot starts and waits for events (main.go)
```

Interact with the bot:

| Command | Expected reply |
|---------|----------------|
| `/start` | `Hi, I'm smaystr-bot!` |
| `/ping`  | `pong` |

## Docker

```bash
# build image (multi-stage, ~10 MB runtime)
docker build -t smaystr-bot .

# run
docker run -e TELE_TOKEN=123456:ABC-DEF smaystr-bot
```

Image використовує distroless-базу, тому всередині лише статичний binary — мінімум CVE та залежностей.

### Docker Compose

Якщо користуєшся `docker compose`, достатньо:

```bash
cp env.example .env   # або свій токен одразу в echo
docker compose up -d  # збирання та запуск

# логи в реальному часі
docker compose logs -f bot
```

## Running Tests

```bash
make test          # or simply `go test ./...`
```

## Temporary Directory Issues

If you encounter an error like:
```
[Errno 2] No usable temporary directory found in ['/tmp', '/var/tmp', '/usr/tmp', ...]
```

You have several options to fix this:

### Option 1: Use the wrapper script
```
./start_with_tmp.sh <your-command>
```

For example:
```
./start_with_tmp.sh go test ./...
./start_with_tmp.sh python -c "import tempfile; print(tempfile.gettempdir())"
```

### Option 2: Import the Python patch directly
For Python code, add this at the beginning of your main file:
```python
import setup_env  # Налаштує тимчасові каталоги
# Ваш код далі...
```

### Option 3: For edX/GlobalLogic Python Tests
For tests in GlobalLogic environment, use the aggressive tempfile patch:
```python
import xqwatcher_tempfile_patch
# Ваш код далі...
```

This patch completely replaces the Python tempfile module with a custom implementation that:
1. Checks multiple possible temp directories, including the current directory
2. Creates missing directories if needed with proper permissions
3. Falls back to a `.xqtmp` directory in the current working directory if all else fails

This is particularly helpful in restricted environments where standard temporary directories might not be accessible.

## Project Layout

```
.
├── cmd/            # CLI entry-points (main package)
│   └── root.go
├── internal/
│   └── bot/        # core bot logic   
│       ├── bot.go
│       └── bot_test.go
├── .gitignore
├── go.mod / go.sum
└── README.md
```

## Extending

1. Add a new handler in `internal/bot/bot.go`, e.g.
   ```go
   b.Telebot.Handle("/ping", func(c tb.Context) error {
       return c.Send("pong")
   })
   ```
2. Create tests in `internal/bot/…_test.go`.
3. Re-run `go test ./...`.

## Contributing

Pull requests are welcome!  
Open an issue first to discuss substantial changes.

## License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/smaystr/smaystr-bot.git
   cd smaystr-bot
```

## Конфігурація через .env

Для зручності всі чутливі дані (токени, паролі) зберігаються у файлі `.env`, який **не комітиться** у git (див. `.gitignore`).
Зразок — у `env.example`:

```env
# Copy to .env and set your real Telegram Bot token
TELE_TOKEN=<YOUR_TELEGRAM_BOT_TOKEN>
```

### Як використовувати .env

- **docker compose** автоматично підтягує `.env` з кореня проєкту:
  ```bash
  docker compose up -d
  ```
- **docker run** — треба явно вказати:
  ```bash
  docker run --env-file .env smaystr-bot:latest
  ```
- **Передати змінну напряму**:
  ```bash
  docker run -e TELE_TOKEN=<YOUR_TELEGRAM_BOT_TOKEN> smaystr-bot:latest
  ```

### Оновлення токена

1. Змініть значення у `.env`:
   ```
   TELE_TOKEN=<NEW_TOKEN>
   ```
2. Перезапустіть контейнер:
   ```bash
   docker compose up -d
   ```

### Безпека

- `.env` завжди має бути у `.gitignore`.
- Не вставляйте реальні токени у Dockerfile чи docker-compose.yml.

---

## Робота з git та тегами

Для фіксації стабільних версій використовуй git tags. Наприклад, щоб створити тег `v1.0.6`:

```bash
git add .
git commit -m "Release v1.0.6: оновлення Dockerfile, Makefile, README"
git tag v1.0.6
git push origin main --tags
```

Тег автоматично підтягується у Makefile для білду версії.

---

## Makefile: основні цілі

```makefile
format:         # Форматує Go-код
deps:           # Оновлює та завантажує залежності
lint:           # Запускає staticcheck
test:           # Запускає всі тести з race-детектором
build:          # Білдить під GOOS/GOARCH, підставляє версію
image:          # Збирає Docker-образ з тегом
push:           # Пушить образ у реєстр
clean:          # Видаляє білд-файл і build-директорію
docker-build:   # Збирає Docker-образ latest
```

Змінні:
- `APP` — ім'я бінарника/образу (за замовчуванням smaystr-bot)
- `REGISTRY` — твій docker registry (локально smaystr)
- `VERSION` — git tag + hash (автоматично)
- `GOARCH`, `TARGETOS` — для мультиархітектурних білдів

Типові сценарії:
```bash
make build         # білдить Go-бінарник
make image         # білдить Docker-образ з версією
make push          # пушить образ у реєстр
make test          # всі тести з race
make lint          # лінтер
```

---

## Кроскомпіляція

Для збирання Go-бінарника під різні платформи використовуйте відповідні цілі Makefile:

```bash
make build-linux-amd64     # Linux x86_64
make build-linux-arm64     # Linux ARM64
make build-darwin-amd64    # macOS x86_64
make build-darwin-arm64    # macOS ARM (Apple Silicon)
make build-windows-amd64   # Windows x86_64 (exe)
```

Усі білди з'являться у поточній директорії з відповідним суфіксом у назві файлу.

## Перевірка локальних Docker-образів

Щоб швидко побачити всі локальні теги для smaystr-bot, скористайся ціллю Makefile:

```bash
make images
```

Вивід покаже всі теги, digest (hash) і розмір кожного образу. Це зручно для контролю, які версії вже зібрані та які теги вказують на один і той самий binary.

## GlobalLogic / edX - Проблема з тимчасовими директоріями

Якщо у вас виникає помилка:
```
[Errno 2] No usable temporary directory found in ['/tmp', '/var/tmp', '/usr/tmp', '/edx/app/xqwatcher/src']
```

Ця проблема автоматично вирішується в репозиторії завдяки наступним механізмам:

1. `sitecustomize.py` - автоматично імпортується Python при запуску і налаштовує тимчасові директорії
2. `Dockerfile` - налаштовує контейнер для правильної роботи з тимчасовими директоріями
3. `pyproject.toml` - забезпечує правильне налаштування Python проекту

При клонуванні репозиторію через GlobalLogic все має працювати автоматично без додаткових дій.