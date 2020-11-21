"""
TODO

- Implement constants file or default config file.
- Implement universal API requests functions.
- Improve error handler.
- Implement custom error for API 400+ status.

PLAN

- command `mcbranch`
- send embed in same channel
- list user in #applicant-forms
- change user's discord nickname to in-game username
- send `whitelist add <in-game username>` in mc server console channel

- when a user leaves, send `whitelist remove <nickname>` in mc server console channel

"""
import logging
from datetime import datetime
from typing import Optional

from discord import Colour, Embed, Member, Role, TextChannel
from discord.ext.commands import Bot, Cog, command, Context


logger = logging.getLogger("bot." + __name__)

VERIFICATION_MESSAGE = (
    "Please verify this information is correct. If there are any mistakes, please correct and re-run the command. "
    "Include a note about having had to re-run the command."
)

APPLICANT_FORM_MESSAGE = "{author} added the following user to the MC branch:"

WHITELIST_MESSAGE = "whitelist add {username}"
REMOVE_WHITELIST_MESSAGE = "whitelist remove {username}"


class Recruit(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @property
    def minecraft_console_channel(self) -> Optional[TextChannel]:
        return self.bot.get_channel(self.bot.conf["MINECRAFT_CONSOLE_CHANNEL_ID"])

    @property
    def survival_minecraft_role(self) -> Optional[Role]:
        guild = self.bot.get_guild(self.bot.conf["GUILD_ID"])
        return guild.get_role(self.bot.conf["SURVIVAL_MINECRAFT_ROLE_ID"])

    async def is_game_username_valid(self, username: str) -> bool:
        """Check if minecraft username is valid."""
        url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
        async with self.bot.http_session.get(url) as response:
            if response.status == 200:
                return True
            return False

    @staticmethod
    def build_applicant_embed(title: str, **applicant_data) -> Embed:
        """Build the new applicant embed."""
        embed = Embed(color=Colour.green())
        embed.title = "Applicant data"
        embed.description = f"{title}\n\n"
        for key, value in applicant_data.items():
            embed.description += f"**{key}:** {value}\n"

        embed.set_footer(text=f"{str(datetime.utcnow().replace(microsecond=0, second=0))} UTC.")

        return embed

    @command(name="mcbranch")
    async def mc_branch(self, ctx: Context, user: Member, game_username: str, age: int, *, notes: str) -> None:
        """Add a user to the minecraft survival branch."""
        # Verify game username
        if not await self.is_game_username_valid(game_username):
            await ctx.send("Minecraft username not found!")
            return

        # build verification embed
        applicant_data = {
            "Minecraft Username": game_username,
            "Discord Username": user.mention,
            "Reported Age": age,
            "Notes": notes
        }
        embed = self.build_applicant_embed(VERIFICATION_MESSAGE, **applicant_data)
        await ctx.send(embed=embed)

        # Change user's nick to minecraft username
        await user.edit(nick=game_username)

        # Give the user survival minecraft role
        await user.add_roles(self.survival_minecraft_role)

        # List new user in #applicant-forms channel
        applicant_forms_channel = self.bot.get_channel(self.bot.conf["APPLICANT_FORMS_CHANNEL_ID"])
        await applicant_forms_channel.send(embed=self.build_applicant_embed(
                APPLICANT_FORM_MESSAGE.format(author=ctx.author.mention),
                **applicant_data
            )
        )

        # Whitelist user on the server
        await self.minecraft_console_channel.send(WHITELIST_MESSAGE.format(username=game_username))

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        """Blacklist user from minecraft survival server."""
        if self.survival_minecraft_role in member.roles:
            await self.minecraft_console_channel.send(REMOVE_WHITELIST_MESSAGE.format(username=member.nick))


def setup(bot: Bot) -> None:
    """Setup Cog."""
    bot.add_cog(Recruit(bot))
    logger.info("Recruit Cog loaded.")
