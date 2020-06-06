from random import randint
from humanize import naturaltime
from discord.ext import commands
from typing import Union, Optional
from discord import User, Embed, Member, Status, Colour, HTTPException


class GeneralCog(commands.Cog):
    """Cog used for general commands that don't belong anywhere specific."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def info(self, ctx, *, snwflk: Union[Member, int] = None):
        try:
            snwflk = ctx.guild.get_member(getattr(snwflk, 'id', snwflk)) or await self.bot.fetch_user(snwflk)
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
            for i in (1, 3):
                embed.remove_field(i)

            if ctx.guild:
                embed.set_footer(text='This user is not in this guild.')

        if snwflk is ctx.guild.me:
            async with self.bot.session.get(
                    "https://raw.githubusercontent.com/Py-Ryan/ftg-rewrite/master/README.md") as get:
                version = (await get.text()).split("\n")[4]
                embed.set_footer(text=f'Developer: well in that case#0082 (700091773695033505) | Version: {version}')

        await ctx.send(embed=embed)

    @commands.command(aliases=['avatar', 'pfp'])
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def av(self, ctx, *, user: Optional[User]):
        user = user or ctx.author

        embed = (
            Embed(title=f'{user}\'s avatar:', colour=randint(0, 0xffffff))
            .set_image(url=str(user.avatar_url_as(static_format='png')))
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GeneralCog(bot))
