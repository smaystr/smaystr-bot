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

# 3. export your token (fish/zsh/bash)
$ export TELE_TOKEN="123456:ABC-DEF…"

# 4. run
$ go run .            # bot starts and waits for events (main.go)
```

Interact with the bot:

| Command | Expected reply |
|---------|----------------|
| `/start` | `Hi, I'm smaystr-bot!` |
| `/ping`  | `pong` |

## Running Tests

```bash
make test          # or simply `go test ./...`
```

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