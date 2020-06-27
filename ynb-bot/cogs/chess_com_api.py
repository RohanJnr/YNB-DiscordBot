import logging

from discord.ext.commands import Cog, Bot


logger = logging.getLogger("bot" + __name__)


class ChessComAPI(Cog):
    """
    Retrieve data from the Chess.com API.

    TODO: UTILS
    - Access Chess.com account with discord ID
    - discord account id - chess username

    TODO: COMMANDS
    - Player profile + Player online status
    - Clubs/team
    - Tournaments
    - Random puzzle

    TODO: TIMED TASKS
    - Send daily puzzle in TextChannel
    """
    def __init__(self, bot: Bot) -> None:
        self.bot = bot


def setup(bot: Bot) -> None:
    bot.add_cog(ChessComAPI(bot))




