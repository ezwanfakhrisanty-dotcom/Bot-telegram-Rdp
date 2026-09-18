# Telegram RDP Bot + GitHub Actions

This project connects a Telegram bot to a GitHub Actions Windows runner.

## GitHub Secrets

Add these repository secrets:

- `GITHUB_TOKEN` — token that can dispatch Actions workflows in the repository.
- `TAILSCALE_AUTH_KEY` — Tailscale auth key for your own tailnet.
- `TELEGRAM_BOT_TOKEN` — token from BotFather.
- `TELEGRAM_CHAT_ID` — Telegram chat ID that receives the RDP details.

For the bot process itself, set:

- `TELEGRAM_BOT_TOKEN`
- `GITHUB_TOKEN`
- `GITHUB_REPO` (example: `username/repository`)
- optional `WORKFLOW_FILE=rdp.yml`
- optional `ALLOWED_CHAT_IDS=123456789`

## Run the bot

```bash
pip install -r requirements.txt
python bot.py
```

The bot supports `/create`, `/status`, and `/help`.

The workflow intentionally uses a bounded runtime. It is not designed to bypass GitHub Actions limits or keep a runner alive indefinitely.
