package bot

import (
	"errors"
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"
	tb "gopkg.in/telebot.v4"
)

// mockContext emulates telebot.Context, overriding only Send.
// It is sufficient for testing outgoing text without relying on Telegram API.
type mockContext struct {
	// embedded interface provides the remaining methods
	tb.Context
	sentMessage string
	sendErr     error
}

func (m *mockContext) Send(v interface{}, _ ...interface{}) error {
	if m.sendErr != nil {
		return m.sendErr
	}
	s, ok := v.(string)
	if !ok {
		return fmt.Errorf("not a string: %T", v)
	}
	m.sentMessage = s
	return nil
}

// Ensure mockContext still implements the full telebot.Context interface.
var _ tb.Context = (*mockContext)(nil)

func TestBot_HandleStart(t *testing.T) {
	cases := []struct {
		name     string
		botName  string
		wantText string
		sendErr  error
		wantErr  bool
	}{
		{
			name:     "default name",
			botName:  "smaystr-bot",
			wantText: "Hi, I'm smaystr-bot!",
			wantErr:  false,
		},
		{
			name:     "custom name",
			botName:  "demo",
			wantText: "Hi, I'm demo!",
			wantErr:  false,
		},
		{
			name:     "send error",
			botName:  "failbot",
			wantText: "", // message ignored on error
			sendErr:  errors.New("mock send failure"),
			wantErr:  true,
		},
	}

	for _, tc := range cases {
		tc := tc // capture range variable
		t.Run(tc.name, func(t *testing.T) {
			b := NewBot(nil, tc.botName)
			ctx := &mockContext{sendErr: tc.sendErr}

			err := b.HandleStart(ctx)
			if tc.wantErr {
				require.Error(t, err)
				return
			}
			require.NoError(t, err)
			require.Equal(t, tc.wantText, ctx.sentMessage)
		})
	}
}
