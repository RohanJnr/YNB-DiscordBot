import asyncio
import logging
from datetime import datetime, timedelta, time
from pathlib import Path

from discord import TextChannel, Message, Embed, Colour, HTTPException, File
from discord.ext.commands import Bot, Cog


logger = logging.getLogger("bot." + __name__)

ONE_WEEK: timedelta = timedelta(days=7)


class Clean(Cog):
    """Clean channels by applying specific filters."""
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @staticmethod
    def time_until_midnight() -> int:
        """Calculate time until UTC midnight."""
        now: datetime = datetime.utcnow()
        midnight_time: time = time(19, 0, 0)
        midnight: datetime = datetime.combine(now, midnight_time)

        return (midnight - now).seconds

    async def clean_gallery(self) -> None:
        """Remove messages except images from #gallery channel."""
        logger.info("CLEAN GALLERY loop running!")
        gallery_channel: TextChannel = await self.bot.fetch_channel(self.bot.conf["GALLERY_CHANNEL_ID"])
        reporting_channel: TextChannel = await self.bot.fetch_channel(self.bot.conf["BOT_STATS_ID"])

        while not self.bot.is_closed():
            logger.info("Purging Messages...")

            def filter_msgs(m: Message) -> bool:
                # Do not delete message which has an attachment, eg: image.
                if m.attachments:
                    return False
                return True

            current_time: datetime = datetime.utcnow()

            week_before: datetime = current_time - ONE_WEEK

            deleted_messages: list = await gallery_channel.purge(
                limit=None,
                check=filter_msgs,
                after=week_before
            )

            logger.info(f"{len(deleted_messages)} have been deleted.")

            if deleted_messages:
                embed: Embed = Embed(colour=Colour.red())
                embed.title = f"{len(deleted_messages)} Messages have been deleted."
                embed.description = ""
                for message in deleted_messages:
                    embed.description += f"\n**From: {message.author}**\n{message.content}\n"

                try:
                    await reporting_channel.send(embed=embed)
                except Exception as e:
                    if isinstance(e, HTTPException):
                        logger.warning("Embed Body too long for reporting message, sending file instead.")
                        deleted_messages_file = Path("deleted_messages.txt")
                        deleted_messages_file.write_text(embed.description)
                        file_object = File(fp=str(deleted_messages_file), filename="Deleted messages")
                        await reporting_channel.send(file=file_object)


            else:
                await reporting_channel.send("0 Messages have been deleted.")

            sleep_for: int = self.time_until_midnight()
            minutes, seconds = divmod(sleep_for, 60)
            hours, minutes = divmod(minutes, 60)
            logger.info(f"Purging again in {hours} hours {minutes} minutes.")
            await reporting_channel.send(f"```Purging again in {hours} hours {minutes} minutes.```")
            await asyncio.sleep(sleep_for)


def setup(bot: Bot) -> None:
    bot.loop.create_task(Clean(bot).clean_gallery())

    bot.add_cog(Clean(bot))
    logger.info("Clean Cog loaded.")
