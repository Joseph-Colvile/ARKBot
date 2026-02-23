# ARK Nitrado Discord Bot (Container-ready)

This bot provides Discord slash commands to control a Nitrado-hosted ARK server:

- `/ark-status` → show current status
- `/ark-on` → send start command
- `/ark-off` → send stop command

It also supports optional timed status updates to a Discord channel.

## 1) Create Discord bot + get IDs

1. Go to Discord Developer Portal and create an application.
2. Add a bot user and copy the bot token.
3. In **OAuth2 > URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Bot permissions: `Send Messages`, `Use Slash Commands`
4. Invite the bot to your server with the generated URL.
5. Enable Developer Mode in Discord and copy:
   - Your server (guild) ID
   - Optional status channel ID

## 2) Nitrado API details

You need:

- `NITRADO_TOKEN`: API token from your Nitrado account
- `NITRADO_SERVICE_ID`: the service ID for your ARK server

## 3) Configure environment

Copy `.env.example` to `.env` and fill values:

```env
DISCORD_BOT_TOKEN=...
DISCORD_GUILD_ID=...
NITRADO_TOKEN=...
NITRADO_SERVICE_ID=...
STATUS_CHANNEL_ID=...
STATUS_UPDATE_INTERVAL_MINUTES=10
```

`STATUS_CHANNEL_ID` is optional. If blank, scheduled status posts are disabled.

For safer secret handling, you can use file-based secrets instead of plain tokens:

- `DISCORD_BOT_TOKEN_FILE=./secrets/discord_bot_token.txt`
- `NITRADO_TOKEN_FILE=./secrets/nitrado_token.txt`

The app accepts either `*_TOKEN` or `*_TOKEN_FILE`.

## 4) Run with Docker

```bash
docker compose up -d --build
```

## 5) Home Assistant (Container)

If you run Home Assistant in Docker, you can run this as a side container:

- Put this project folder on the same host as Home Assistant.
- Ensure `.env` exists with real values.
- Start with `docker compose up -d --build`.
- Add `restart: unless-stopped` (already included) so it comes back after host reboot.

## 6) Home Assistant Add-on (OS / Supervised)

This repository is now structured as a Home Assistant Git add-on repository:

- `repository.yaml` (required by Home Assistant)
- `ark-nitrado-discord/` (the add-on folder)

Before adding the repository in Home Assistant, set your real repository URL in [repository.yaml](repository.yaml).

PowerShell quick update example:

```powershell
$repo = "https://github.com/<you>/<repo>"
(Get-Content repository.yaml) -replace "https://github.com/your-user/your-repo", $repo | Set-Content repository.yaml
```

Install from Git by:

1. Push this project to a Git repository.
2. In Home Assistant UI: **Settings → Add-ons → Add-on Store**.
3. Click menu (⋮) → **Repositories**.
4. Add your Git URL (for example: `https://github.com/<you>/<repo>`), then **Add**.
5. Find **ARK Nitrado Discord Bot** in the store, open it, set config values, and start it.

For Git-safe secret handling in the add-on, use one of these approaches:

- Enter `discord_bot_token` and `nitrado_token` directly in add-on Configuration (stored in Home Assistant, not in your Git repo), or
- Set `discord_bot_token_file` and `nitrado_token_file` to file paths under `/config` (for example `/config/secrets/discord_bot_token.txt`).

You can still install locally by copying `ark-nitrado-discord/` into `/addons/local/ark-nitrado-discord`.

## Notes

- Slash commands are synced to `DISCORD_GUILD_ID` for fast updates while developing.
- Start/stop can take time on Nitrado side; use `/ark-status` to check progress.
