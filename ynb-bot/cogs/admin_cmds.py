import logging
from datetime import datetime, timedelta

from discord import TextChannel, Guild, Role
from discord.ext.commands import Cog, Bot, command, has_role


logger = logging.getLogger("bot." + __name__)


class AdminCmds(Cog):
    """Admin commands."""
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(name="update-verified")
    @has_role(554485497192513540)
    async def assing_verified_role(self, ctx):
        """Assign the verified role to members who have been on the server for more than 30 days."""
        reporting_channel: TextChannel = await self.bot.fetch_channel(self.bot.conf["BOT_STATS_ID"])
        smp_role_id: int = 489176009120415744
        verified_role_id: int = 705274433723564083
        nverfied_members: list = []
        guild: Guild = ctx.guild
        all_members: list = guild.members
        for member in all_members:
            member_join_date: datetime = member.joined_at
            today: datetime = datetime.now()
            days_present: timedelta = today - member_join_date

            roles_id: list = [role.id for role in member.roles]
            if smp_role_id in roles_id:
                if days_present.days > 29:
                    verified_role: Role = guild.get_role(verified_role_id)
                    await member.add_roles(verified_role)
                    logger.info(f"{str(member)} is given the {verified_role.name} role.")
                    nverfied_members.append(str(member))
                else:
                    pass

        msg: str = f"**{len(nverfied_members)} have been given the verified role.**\n\n"
        for m in nverfied_members:
            msg += m

        await reporting_channel.send(msg)


def setup(bot: Bot) -> None:
    bot.add_cog(AdminCmds(bot))
    logger.info("Admin cmds Cog loaded.")




