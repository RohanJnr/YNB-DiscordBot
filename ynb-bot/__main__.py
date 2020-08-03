import logging
from datetime import datetime
from json import load
from pathlib import Path


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

today = datetime.today()

log_file = Path("logs", f"logging{str(today)}.txt")

log_file.parent.mkdir(exist_ok=True)

file_logging = logging.FileHandler(log_file)
file_logging.setFormatter(formatter)

logger.addHandler(console_logging)
logger.addHandler(file_logging)

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

        self.load_extension("ynb-bot.cogs.clean")
        self.load_extension("ynb-bot.cogs.server_info")
        self.load_extension("ynb-bot.cogs.error_handler")
        self.load_extension("ynb-bot.cogs.lichess_api")
        self.load_extension("ynb-bot.cogs.admin_cmds")
        self.load_extension("ynb-bot.cogs.clock_channel")

        logger.info("Loading cogs... DONE\n")

        await self.change_presence(activity=Game(name="You Need Beer!"))


if __name__ == "__main__":
    bot = YnbBot()
    bot.run(BOT_TOKEN)
