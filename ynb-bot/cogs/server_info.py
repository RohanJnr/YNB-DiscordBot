import logging
import typing
from datetime import datetime, timedelta

from discord import Member, Role
from discord.ext.commands import command, Context, Cog, Bot, group


logger = logging.getLogger("bot." + __name__)


class ServerInformation(Cog):
    """Information regarding general server attributes."""
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @group(name="members", invoke_without_command=True)
    async def members_info(self, ctx: Context) -> None:
        """Information about the server members with filters."""
        await ctx.send_help(ctx.command)

    @members_info.command(name="list")
    async def list_members(self, ctx: Context, role_id: typing.Optional[int], filter_type: str, date_or_day: str) -> None:
        """
        List server memebrs with datetime filters.

        Filter options:
        - before : members who joined before a date(yyyy-mm-dd)
        - after : members who joined after a date(yyyy-mm-dd)
        - aged : members who have been on the server for x number of days or more/less.

        Example usage:
        .members list before 2020-10-13
        - lists all members who joined before this date.

        .members list after 2020-10-13
        - lists all members who joined after this date.

        .members list aged 7>
        - lists all members who have been on the server for more than 7 days.

        .members list aged 7<
        - lists all members who have been on the server for less than 7 days.

        Want to add role filtering? Sure!
        - Add the role ID before the filter_type
        example: .members list 3052305320 aged 7<
        """
        filtered_members: list = []
        members: list = ctx.guild.members

        if role_id:
            role: Role = ctx.guild.get_role(role_id)
            if role:
                members = [member for member in members if role in member.roles]
            else:
                await ctx.send("Invalid Role ID.")
                return

        if filter_type in ["before", "after"]:
            try:
                date: datetime = datetime(*[int(i) for i in date_or_day.split("-")])
            except ValueError as e:
                await ctx.send(f"```Invalid Date !\n {e}```")
                return
            for member in members:

                if filter_type == "before":
                    if date > member.joined_at:
                        filtered_members.append(member)

                else:  # filter_type=after
                    if member.joined_at > date:
                        filtered_members.append(member)

        elif filter_type == "aged":
            today: datetime = datetime.today()
            days: int = int(date_or_day[0:-1])
            operator: str = date_or_day[-1]

            if operator not in [">", "<"]:
                await ctx.send("```Invalid Aged Filter !!\nAvailable options:\n>\n<```")
                return

            for member in members:

                diff: timedelta = today - member.joined_at

                if operator == "<":
                    if diff.days < days:
                        filtered_members.append(member)

                elif operator == ">":
                    if diff.days > days:
                        filtered_members.append(member)

        else:
            await ctx.send("```Invalid Filter !!```")

        msg = f"```**FILTERED LIST OF MEMBERS - {len(filtered_members)} found**\n\n"

        if filtered_members:
            for filtered_member in filtered_members:
                msg += f"{filtered_member} \n"

            msg += "```"
            await ctx.send(msg)
        else:
            await ctx.send("```0 Members found.```")


def setup(bot: Bot) -> None:
    """Setup Cog."""
    bot.add_cog(ServerInformation(bot))
    logger.info("ServerInformation Cog loaded.")
