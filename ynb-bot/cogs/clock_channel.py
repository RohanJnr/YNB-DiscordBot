import asyncio
import logging
import typing
from datetime import datetime

from discord import TextChannel
from discord.ext.commands import Bot, Cog


logger = logging.getLogger("bot." + __name__)

CLOCK_EMOJIS: typing.Dict[str: str] = {
    "clock12": "🕐\U0001f55b",
    "clock1230": "🕐\U0001f567",
    "clock1": "🕐\U0001f550",
    "clock130": "🕐\U0001f55c",
    "clock2": "🕐\U0001f551",
    "clock230": "🕐\U0001f55d",
    "clock3": "🕐\U0001f552",
    "clock330": "🕐\U0001f55e",
    "clock4": "🕐\U0001f553",
    "clock430": "🕐\U0001f55f",
    "clock5": "🕐\U0001f554",
    "clock530": "🕐\U0001f560",
    "clock6": "🕐\U0001f555",
    "clock630": "🕐\U0001f561",
    "clock7": "🕐\U0001f556",
    "clock730": "🕐\U0001f562",
    "clock8": "🕐\U0001f557",
    "clock830": "🕐\U0001f563",
    "clock9": "🕐\U0001f558",
    "clock930": "🕐\U0001f564",
    "clock10": "🕐\U0001f559",
    "clock1030": "🕐\U0001f565",
    "clock11": "🕐\U0001f55a",
    "clock1130": "\U0001f566"
}


class ClockChannel(Cog):
    """Configure Clock voice channel to display UTC time."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def config_clock_channel(self):
        """Change clock voice channel name to comply with current UTC time."""
        clock_channel_id: int = self.bot.conf["CLOCK_CHANNEL_ID"]
        while not self.bot.is_closed():
            utc_time: datetime = datetime.utcnow()

            hour: int = utc_time.hour
            minutes: int = utc_time.minute

            time_to_display: str = f"{hour}:{minutes}"

            if hour > 12:
                hour = hour-12

            if minutes < 30:
                emoji_name: str = f"clock{hour}"
            else:
                emoji_name = f"clock{hour}30"

            clock_emoji: str = CLOCK_EMOJIS[emoji_name]
            if len(clock_emoji) == 2:  # bug: why is the length=2?
                clock_emoji = clock_emoji[1]

            channel_name: str = f"{clock_emoji} {time_to_display} UTC"

            channel: TextChannel = await self.bot.fetch_channel(clock_channel_id)
            await channel.edit(name=channel_name)
            await asyncio.sleep(60*5)


def setup(bot: Bot) -> None:
    bot.loop.create_task(ClockChannel(bot).config_clock_channel())

    bot.add_cog(ClockChannel(bot))
    logger.info("ClockChannel cog loaded.")


