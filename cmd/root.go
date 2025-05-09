package cmd

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"time"

	log "github.com/sirupsen/logrus"

	"github.com/smaystr/smaystr-bot/internal/bot"
	"github.com/spf13/cobra"
	tb "gopkg.in/telebot.v4"
)

var rootCmd = &cobra.Command{
	Use:   "smaystr-bot",
	Short: "Telegram bot for smaystr",
	RunE: func(cmd *cobra.Command, args []string) error {
		token := os.Getenv("TELE_TOKEN")
		if token == "" {
			return fmt.Errorf("TELE_TOKEN is not set")
		}

		tbot, err := tb.NewBot(tb.Settings{
			Token:  token,
			Poller: &tb.LongPoller{Timeout: 10 * time.Second},
		})
		if err != nil {
			log.WithError(err).Error("failed to create bot")
			return fmt.Errorf("create bot: %w", err)
		}

		myBot := bot.New(tbot, "smaystr-bot")
		myBot.RegisterHandlers()

		// graceful shutdown on Ctrl-C
		ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
		defer stop()

		go func() {
			<-ctx.Done()
			tbot.Stop()
		}()

		log.Info("Bot started…")
		tbot.Start()
		return nil
	},
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		log.Fatal(err)
	}
}
