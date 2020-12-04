import logging
from urllib.parse import urlparse

import aiohttp
from discord import Message
from discord.ext.commands import Bot, Cog


logger = logging.getLogger("bot." + __name__)

EMOJIS = {}


class Events(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def load_emojis(self):
        """Cache all emojis."""
        guild = self.bot.get_guild(self.bot.conf["GUILD_ID"])
        for emoji_name, value in self.bot.conf["EMOJIS"].items():
            if isinstance(value, int):
                EMOJIS[emoji_name] = await guild.fetch_emoji(value)
            else:
                EMOJIS[emoji_name] = value

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """Trigger this function when a message is sent in the guild."""
        if message.channel.id == self.bot.conf["MEMES_CHANNEL_ID"]:
            if await self.has_link(message) or message.attachments:
                # Add all emojis
                for emoji in EMOJIS.values():
                    await message.add_reaction(emoji)

        elif message.channel.id == self.bot.conf["FEEDBACK_CHANNEL_ID"]:
            # Add all except LMFAO
            for emoji_name, value in EMOJIS.items():
                if emoji_name in ["LMFAO_EMOJI_ID"]:
                    continue
                await message.add_reaction(value)

    async def has_link(self, message):
        """Check if message contains a link."""
        words: list = message.content.split()
        links = [word for word in words if urlparse(word).scheme in ["https", "http"]]
        if links:
            return await self.verify_url(links)
        return False

    @staticmethod
    async def verify_url(links: list) -> bool:
        """Check if URL exists."""
        for index, link in enumerate(links):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(link) as resp:
                        if resp.status == 200:
                            return True
                        return False
            except Exception as e:
                logger.error(str(e))
                return False


def setup(bot: Bot):
    bot.add_cog(Events(bot))
    bot.loop.create_task(Events(bot).load_emojis())
    logger.info("Events cog loaded.")
