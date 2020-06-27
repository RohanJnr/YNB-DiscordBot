import logging

from discord.ext import commands


logger = logging.getLogger('bot.' + __name__)


class ErrorHandler(commands.Cog):
    """Cog to handle errors."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Fires when a command throws an error."""
        logger.error(str(error))
        await ctx.send(f"```{error}```")


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
    logger.info("ErrorHandler Cog loaded")