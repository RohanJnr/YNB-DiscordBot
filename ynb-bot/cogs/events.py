import logging

import aiohttp
from discord import Message
from discord.ext.commands import Bot, Cog


logger = logging.getLogger("bot." + __name__)

EMOJIS: list = []


class Events(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def load_emojis(self):
        guild = self.bot.get_guild(self.bot.conf["GUILD_ID"])
        for emoji_name, value in self.bot.conf["EMOJIS"].items():
            if isinstance(value, int):
                EMOJIS.append(await guild.fetch_emoji(value))
            else:
                EMOJIS.append(value)

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        await self.add_reactions(message)

    async def add_reactions(self, message):
        """Add reactions to messages in #memes channel."""
        if message.channel.id == self.bot.conf["MEMES_CHANNEL_ID"]:
            if await self.has_link(message) or message.attachments:
                for emoji in EMOJIS:
                    await message.add_reaction(emoji)

    async def has_link(self, message):
        """Check if message contains a link."""
        words: list = message.content.split()
        links = [word for word in words if word.startswith("https://")]
        if links:
            return await self.verify_url(links)
        return False

    @staticmethod
    async def verify_url(links):
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
