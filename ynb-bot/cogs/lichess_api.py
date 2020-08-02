import asyncio
import logging
from json import dump, load
from pathlib import Path
from typing import Union, List, Optional, Dict

import aiohttp
from discord import Member, Embed, Colour, TextChannel
from discord.ext.commands import Cog, Bot, group, Context


logger = logging.getLogger("bot." + __name__)


class LichessAPI(Cog):
    """
    Retrieve data from the lichess.com API.
    """
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.json_file = Path("ynb-bot", "resources", "lichess.json")
        self.linked_users = self.get_linked_users()

    @staticmethod
    async def fetch(session: aiohttp.ClientSession, url: str, params=None) -> Union[dict, None]:
        headers: dict = {
            "Accept": 'application/json'
        }
        try:
            async with session.get(url=url, params=params, headers=headers) as response:
                return await response.json(content_type=None)
        except Exception as e:
            logger.error(f"API request error: {e}")
            return None

    async def _get_user(self, username: str) -> Union[dict, None]:
        """Fetch User details."""
        url: str = f"https://lichess.org/api/user/{username}"
        async with aiohttp.ClientSession() as session:
            response: Union[dict, None] = await self.fetch(session, url)
            return response

    @group(name="lichess", invoke_without_command=True)
    async def lichess(self, ctx: Context) -> None:
        """Contains commands that access lichess API."""
        await ctx.send_help(ctx.command)

    @lichess.command(name="link")
    async def link_account(self, ctx: Context, username: str) -> None:
        """Link lichess account with your discord."""
        linked_usernames: List[str] = list(self.linked_users.keys())

        if username.lower() in linked_usernames:
            linked_discord_user: Member = self.bot.get_user(self.linked_users[username.lower()])
            await ctx.send(f"```{username} is already linked with discord user {linked_discord_user}```")
            return

        user: Union[dict, None] = await self._get_user(username)
        if user:
            self.linked_users[username.lower()] = ctx.author.id
            self.update_linked_users()
            await ctx.send("```Account Linked Successfully.```")
        else:
            await ctx.send("```Invalid Username.```")
            return

    @lichess.command(name="unlink")
    async def unlink_account(self, ctx: Context) -> None:
        """Link lichess account with your discord."""
        linked_discord_ids: List[int] = list(self.linked_users.values())

        if ctx.author.id not in linked_discord_ids:
            await ctx.send("Your discord is not linked to a lichess account.")
            return

        self.linked_users = {key: val for key, val in self.linked_users.items() if val != ctx.author.id}
        self.update_linked_users()
        await ctx.send("```Account Unlinked Successfully.```")

    @lichess.command(name="showall")
    async def show_all_linked_users(self, ctx: Context) -> None:
        """Display all linked users."""
        msg: str = "```Lichess Username - Discord Account\n\n"
        for lichess_username, discord_id in self.linked_users.items():
            discord_member = self.bot.get_user(discord_id)
            msg += f"{lichess_username} - {discord_member}\n"
        msg += "```"
        await ctx.send(msg)

    @lichess.command(name="info")
    async def account_information(self, ctx, discord_user: Optional[Member], lichess_username: str = None) -> None:
        """
        Display Lichess account information.

        target: lichess username or tag the discord user
        """
        if not lichess_username and not discord_user:
            await ctx.send("```Lichess username or tag a discord user is a required parameter.```")
            return

        if lichess_username and not discord_user:
            user: Union[dict, None] = await self._get_user(lichess_username)
        else:
            try:
                lichess_username = {val: key for key, val in self.linked_users.items()}[discord_user.id]
            except KeyError:
                await ctx.send(f"```{discord_user} is not linked to a lichess account.```")
                return
            else:
                user: Union[dict, None] = await self._get_user(lichess_username)

        if not user:
            await ctx.send(f"```User not found.```")
            return

        embed: Embed = self.generate_user_embed(user)
        await ctx.send(embed=embed)

    @staticmethod
    def generate_user_embed(user: dict) -> Embed:
        """Generate embed for Lichess user profile."""
        username: str = user["username"]
        playtime: int = user["playTime"]["total"] // 60  # converting seconds to mintues
        no_of_following: int = user["nbFollowing"]
        no_of_followers: int = user["nbFollowers"]
        no_of_games: int = user["count"]["all"]
        wins: int = user["count"]["win"]
        losses: int = user["count"]["loss"]
        draws: int = user["count"]["draw"]
        url: str = user["url"]

        embed: Embed = Embed(color=Colour.red())
        embed.title = f"```{username} Profile```"
        embed.url = url
        embed.description = f"```Total play time: {playtime} Minutes\n" \
                            f"Followers: {no_of_followers}\n" \
                            f"Following: {no_of_following}\n\n" \
                            f"Total Number of Games: {no_of_games}\n" \
                            f"Wins: {wins}\n" \
                            f"Losses: {losses}\n" \
                            f"Draws: {draws}\n\n```"

        embed.description += f"**Game Modes**\n"
        for game_mode, stats in user["perfs"].items():
            if stats["games"] != 0:
                rating: int = stats["rating"]
                embed.description += f"```**{game_mode}**\n" \
                                     f"Games: {stats['games']}\n" \
                                     f"Rating: {rating}```"

        return embed

    def get_linked_users(self) -> dict:
        """Get linked users from json file."""
        logger.info("Fetching Lichess linked accounts.")
        with self.json_file.open() as f:
            data: dict = load(f)
        return data

    def update_linked_users(self) -> None:
        """Update json file containing user data."""
        logger.info("Updating Lichess json file.")
        with self.json_file.open("w") as f:
            dump(self.linked_users, f, indent=2)

    async def get_ongoing_games(self) -> None:
        """Check status of each user and send link for on-going games."""
        logger.info("Lichess - Get Ongoing Games loop running...")
        chess_channel: TextChannel = self.bot.get_channel(self.bot.conf["CHESS_CHANNEL_ID"])
        games: list = []
        while not self.bot.is_closed():
            async with aiohttp.ClientSession() as session:
                usernames: str = ",".join(list(self.linked_users.keys()))
                url: str = "https://lichess.org/api/users/status"
                params: dict = {
                    "ids": usernames
                }
                all_users_status: dict = await self.fetch(session, url, params)
                if all_users_status is not None:
                    for user_status in all_users_status:
                        if "playing" in user_status:
                            fetch_game_url: str = f"https://lichess.org/api/user/{user_status['name']}/current-game"
                            response: Union[dict, None] = await self.fetch(session, fetch_game_url)
                            if not response:
                                continue
                            game_id: int = response["id"]
                            game_url: str = f"https://lichess.org/{game_id}"
                            if game_url not in games:
                                games.append(game_url)
                                msg: str = f"On Going Match! Spectate now!\n{game_url}"
                                logger.info(f"Lichess Live game found: {game_url}")
                                await chess_channel.send(msg)

            await asyncio.sleep(10)


def setup(bot: Bot) -> None:
    bot.loop.create_task(LichessAPI(bot).get_ongoing_games())
    bot.add_cog(LichessAPI(bot))
    logger.info("LichessAPI cog loaded.")
