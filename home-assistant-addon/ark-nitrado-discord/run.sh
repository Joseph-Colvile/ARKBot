#!/usr/bin/with-contenv bashio
set -euo pipefail

export DISCORD_BOT_TOKEN="$(bashio::config 'discord_bot_token')"
export DISCORD_GUILD_ID="$(bashio::config 'discord_guild_id')"
export NITRADO_TOKEN="$(bashio::config 'nitrado_token')"
export NITRADO_SERVICE_ID="$(bashio::config 'nitrado_service_id')"
export STATUS_UPDATE_INTERVAL_MINUTES="$(bashio::config 'status_update_interval_minutes')"

if bashio::config.has_value 'status_channel_id'; then
  export STATUS_CHANNEL_ID="$(bashio::config 'status_channel_id')"
else
  unset STATUS_CHANNEL_ID || true
fi

cd /app
exec python3 -m bot.main
