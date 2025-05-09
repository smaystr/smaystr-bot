package bot

import (
	tb "gopkg.in/telebot.v4"
)

// Bot wraps the telebot instance with extra metadata.
type Bot struct {
	Telebot *tb.Bot
	Name    string
}

// NewBot returns a new Bot instance.
func NewBot(telebot *tb.Bot, name string) *Bot {
	return &Bot{
		Telebot: telebot,
		Name:    name,
	}
}

// New is an alias to NewBot kept for backward compatibility.
func New(telebot *tb.Bot, name string) *Bot {
	return NewBot(telebot, name)
}

// RegisterHandlers registers all command/message handlers for the bot.
func (b *Bot) RegisterHandlers() {
	if b.Telebot == nil {
		return
	}
	b.Telebot.Handle("/start", b.HandleStart)
	b.Telebot.Handle("/ping", b.HandlePing)
}

// HandleStart responds to the /start command.
func (b *Bot) HandleStart(c tb.Context) error {
	return c.Send("Hi, I'm " + b.Name + "!")
}

// HandlePing responds to /ping command.
func (b *Bot) HandlePing(c tb.Context) error {
	return c.Send("pong")
}
