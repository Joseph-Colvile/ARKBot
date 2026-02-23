# Home Assistant Add-on: ARK Nitrado Discord Bot

This add-on runs a Discord bot that can:

- `/ark-status` show ARK server status
- `/ark-on` start the Nitrado ARK server
- `/ark-off` stop the Nitrado ARK server

## Add-on configuration

Set these in the add-on **Configuration** tab:

- `discord_bot_token`
- `discord_guild_id`
- `nitrado_token`
- `nitrado_service_id`
- `status_channel_id` (optional)
- `status_update_interval_minutes` (default `10`)

## Installation (Home Assistant OS / Supervised)

1. Copy this folder into Home Assistant local addons path:
   - `/addons/local/ark-nitrado-discord`
2. In Home Assistant, go to **Settings → Add-ons → Add-on Store**.
3. Click menu (⋮) → **Reload**.
4. Open add-on **ARK Nitrado Discord Bot**.
5. Configure required options, then **Start**.
6. Check **Logs** for successful startup and command sync.
