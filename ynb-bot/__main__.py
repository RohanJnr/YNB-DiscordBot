import logging
from datetime import datetime
from json import load


from discord import Game
from discord.ext.commands import Bot


with open("conf.json") as f:
    conf = load(f)

BOT_TOKEN = conf["BOT_TOKEN"]

logger = logging.getLogger("bot")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('{asctime} - {name} - {levelname} - {message}', style='{')

console_logging = logging.StreamHandler()
console_logging.setFormatter(formatter)

logger.addHandler(console_logging)

# Silence most of discord logs.

logging.getLogger('discord').setLevel(logging.ERROR)
logging.getLogger('aiosqlite').setLevel(logging.ERROR)
logging.getLogger('websockets').setLevel(logging.ERROR)


class YnbBot(Bot):
    """An instance of the `discord.ext.commands.bot`."""

    def __init__(self, *args, **kwargs):
        self.conf = conf
        super().__init__(
            command_prefix=".",
            case_insensitive=True,
            description="YNB Bot is here !",
            *args,
            **kwargs
        )

    async def on_ready(self):
        """Invoke when bot is ready."""
        logger.info(f"Bot Logged in as: {self.user.name}")
        logger.info(f"Starting Time: {datetime.now()}\n")
        logger.info("Loading cogs...")

        self.load_extension("cogs.clean")

        logger.info("Loading cogs... DONE")

        await self.change_presence(activity=Game(name="You Need Beer!"))


if __name__ == "__main__":
    bot = YnbBot()
    bot.run(BOT_TOKEN)
