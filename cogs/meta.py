from random import randint
from contextlib import suppress
from humanize import naturaltime
from discord.ext import commands
from typing import Union, Optional
from discord import User, Embed, Member, Status, Colour, HTTPException


class Meta(commands.Cog):
    """Cog used for general commands that don't belong anywhere specific."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def info(self, ctx, *, snwflk: Union[Member, int] = None):
        try:
            user_id = getattr(snwflk, 'id', snwflk)
            snwflk = ctx.guild.get_member(user_id) or await self.bot.fetch_user(user_id)
        except HTTPException:
            snwflk = ctx.guild.get_member(self.bot.user.id)

        cases = {
            Status.online: Colour.green(),
            Status.idle: Colour.orange(),
            Status.dnd: Colour.red(),
            Status.offline: Colour.light_grey()
        }

        embed = (
            Embed(
                title=str(snwflk),
                colour=cases[snwflk.status] if not isinstance(snwflk, User) else Colour.dark_grey(),
                description=f'[Avatar Link]({snwflk.avatar_url})'
                if not snwflk.id == self.bot.user.id else
                f'[Source Code](https://github.com/Py-Ryan/ftg-rewrite)'
            )
            .add_field(name='**Account Created**', value=naturaltime(snwflk.created_at), inline=True)
            .add_field(name='**Joined**', value=naturaltime(getattr(snwflk, 'joined_at', 'None')), inline=True)
            .add_field(name='**User ID**', value=snwflk.id, inline=False)
            .add_field(name='**Top Role**', value=str(getattr(snwflk, 'top_role', 'None')), inline=False)
            .set_thumbnail(url=str(snwflk.avatar_url_as(static_format='png')))
        )

        if isinstance(snwflk, User):
            embed.set_footer(text='This user is not in this guild.')
            for i in (-1, -2):
                embed.remove_field(i)

        if snwflk is ctx.guild.me:
            async with self.bot.session.get(
                    "https://raw.githubusercontent.com/Py-Ryan/ftg-rewrite/master/README.md") as get:
                version = (await get.text()).split("\n")[4]

            embed.set_footer(text=f'Developer: well in that case#0082 (700091773695033505) | Version: {version}')

        await ctx.send(embed=embed)

    @commands.command(aliases=['avatar', 'pfp'])
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def av(self, ctx, *, user: Union[User, int]):
        try:
            user_id = getattr(user, 'id', user)
            if not isinstance(user, User):
                user = self.bot.get_user(user_id) or self.bot.fetch_user(user_id)
        except HTTPException:
            await ctx.send("Couldn't find a discord user with that ID.")
        else:
            avatar = str(user.avatar_url_as(static_format='png'))
            embed = (
                Embed(title=f'{user}\'s avatar:', colour=randint(0, 0xffffff), url=avatar)
                .set_image(url=avatar)
            )

            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def prefix(self, ctx, prefix):
        """Edit the prefix for the current guild."""
        message = await ctx.send(f"{ctx.author.mention}, change the guild prefix to `{prefix}`?")

        for reaction in ('✅', '❌'):
            await message.add_reaction(reaction)

        with suppress(TimeoutError):
            (reaction, user) = await self.bot.wait_for(
                'reaction_add',
                check=lambda r, u: u.id == ctx.author.id and str(r) in ('✅', '❌'),
                timeout=15
            )

        if str(reaction) == '\U00002705':
            await self.bot.db.execute(
                """
                INSERT INTO guilds (id, prefix)
                VALUES ($1, $2)
                ON CONFLICT (id)
                DO UPDATE
                SET prefix = $2
                """,
                ctx.guild.id,
                prefix
            )
            self.bot.cache[str(ctx.guild.id)]["prefix"] = prefix
            await ctx.send(f"Changed the prefix for this guild. 👌")
        else:
            await ctx.send(f"Alright then. 👌")


def setup(bot):
    bot.add_cog(Meta(bot))
