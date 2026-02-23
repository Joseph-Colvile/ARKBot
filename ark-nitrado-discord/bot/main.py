from __future__ import annotations

import logging
import os
from datetime import UTC, datetime

import discord
from discord import app_commands
from discord.ext import tasks

from .nitrado import NitradoApiError, NitradoClient, ServerStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("arkbot")


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _format_status(status: ServerStatus) -> str:
    players = (
        f"{status.player_current}/{status.player_max}"
        if status.player_current is not None and status.player_max is not None
        else "Unknown"
    )
    game = status.game_human or "ARK"
    return (
        f"**{game}**\n"
        f"State: **{status.state}**\n"
        f"Query: `{status.query_status or 'unknown'}`\n"
        f"Players: `{players}`"
    )


class ArkBot(discord.Client):
    def __init__(self, nitrado: NitradoClient, guild_id: int, status_channel_id: int | None) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.nitrado = nitrado
        self.guild = discord.Object(id=guild_id)
        self.status_channel_id = status_channel_id

    async def setup_hook(self) -> None:
        self._register_commands()
        self.tree.copy_global_to(guild=self.guild)
        synced = await self.tree.sync(guild=self.guild)
        logger.info("Synced %s command(s)", len(synced))

        if self.status_channel_id is not None:
            status_updater.start()

    async def close(self) -> None:
        if status_updater.is_running():
            status_updater.cancel()
        await self.nitrado.close()
        await super().close()

    def _register_commands(self) -> None:
        @self.tree.command(name="ark-status", description="Show ARK server status", guild=self.guild)
        async def ark_status(interaction: discord.Interaction) -> None:
            await interaction.response.defer(thinking=True)
            try:
                status = await self.nitrado.get_status()
                await interaction.followup.send(_format_status(status))
            except NitradoApiError as exc:
                await interaction.followup.send(f"Unable to fetch status: {exc}")

        @self.tree.command(name="ark-on", description="Start the ARK server", guild=self.guild)
        async def ark_on(interaction: discord.Interaction) -> None:
            await interaction.response.defer(thinking=True)
            try:
                message = await self.nitrado.power_on()
                status = await self.nitrado.get_status()
                await interaction.followup.send(f"{message}\n\n{_format_status(status)}")
            except NitradoApiError as exc:
                await interaction.followup.send(f"Unable to start server: {exc}")

        @self.tree.command(name="ark-off", description="Stop the ARK server", guild=self.guild)
        async def ark_off(interaction: discord.Interaction) -> None:
            await interaction.response.defer(thinking=True)
            try:
                message = await self.nitrado.power_off()
                status = await self.nitrado.get_status()
                await interaction.followup.send(f"{message}\n\n{_format_status(status)}")
            except NitradoApiError as exc:
                await interaction.followup.send(f"Unable to stop server: {exc}")


bot: ArkBot | None = None


@tasks.loop(minutes=max(int(os.getenv("STATUS_UPDATE_INTERVAL_MINUTES", "10")), 1))
async def status_updater() -> None:
    if bot is None or bot.status_channel_id is None:
        return

    channel = bot.get_channel(bot.status_channel_id)
    if channel is None:
        try:
            channel = await bot.fetch_channel(bot.status_channel_id)
        except discord.DiscordException as exc:
            logger.warning("Could not fetch status channel: %s", exc)
            return

    if not isinstance(channel, discord.abc.Messageable):
        return

    try:
        status = await bot.nitrado.get_status()
        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
        await channel.send(f"📡 ARK server status update ({now})\n{_format_status(status)}")
    except (NitradoApiError, discord.DiscordException) as exc:
        logger.warning("Failed to post status update: %s", exc)


@status_updater.before_loop
async def before_status_updater() -> None:
    if bot is not None:
        await bot.wait_until_ready()


def main() -> None:
    global bot

    discord_token = _required_env("DISCORD_BOT_TOKEN")
    guild_id = int(_required_env("DISCORD_GUILD_ID"))
    nitrado_token = _required_env("NITRADO_TOKEN")
    service_id = _required_env("NITRADO_SERVICE_ID")

    status_channel_id_raw = os.getenv("STATUS_CHANNEL_ID", "").strip()
    status_channel_id = int(status_channel_id_raw) if status_channel_id_raw else None

    nitrado = NitradoClient(token=nitrado_token, service_id=service_id)
    bot = ArkBot(nitrado=nitrado, guild_id=guild_id, status_channel_id=status_channel_id)
    bot.run(discord_token)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
