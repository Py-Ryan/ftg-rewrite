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

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def info(self, ctx, *, snwflk: Union[Member, int, str] = None):
        if snwflk == 'me':
            snwflk = ctx.author
        else:
            if not isinstance(snwflk, Member):
                try:
                    snwflk = await self.bot.fetch_user(snwflk)
                except HTTPException:
                    snwflk = ctx.guild.me

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
            version = self.bot.__version__
            embed.add_field(name='**Uptime**', value=self.bot.uptime)
            embed.add_field(name='**Latency**', value=f'{round(self.bot.latency * 1000)}ms', inline=False)
            embed.set_footer(text=f'Developer: well in that case#0082 (700091773695033505) | Version: {version}')

        await ctx.send(embed=embed)

    @info.command(name='cog')
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def info_cog(self, ctx, *, cog='Fun'):
        cog = cog.capitalize()
        info_cog = self.bot.cogs.get(cog, None)

        if info_cog:
            info = (
                Embed(
                    title=cog,
                    description=f'Information on the {cog.lower()} extension.',
                    colour=randint(0, 0xffffff)
                )
                .add_field(name='**Command Count**', value=len(info_cog.get_commands()), inline=True)
                .add_field(name='**Lines Of Code**', value=info_cog.loc, inline=True)
                .set_thumbnail(url=str(self.bot.user.avatar_url_as(static_format='png')))
                .set_footer(text=f'Extension loaded {naturaltime(info_cog._raw_uptime)}.')
            )

            await ctx.send(embed=info)
        else:
            await ctx.reply(f'no cogs named {cog}.')

    @commands.command(aliases=['avatar', 'pfp'])
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def av(self, ctx, *, user: Union[User, int, str] = None):
        if user == 'me' or not user:
            user = ctx.author
        else:
            if not isinstance(user, User):
                try:
                    user = await self.bot.fetch_user(user)
                except HTTPException:
                    user = ctx.author

        avatar = str(user.avatar_url_as(static_format='png'))

        embed = Embed(title=f"{user}'s avatar:", url=avatar)
        embed.set_image(url=avatar)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def prefix(self, ctx, prefix):
        """Edit the prefix for the current guild."""
        message = await ctx.reply(f'change the guild prefix to `{prefix}`?')

        for reaction in ('✅', '❌'):
            await message.add_reaction(reaction)

        with suppress(TimeoutError):
            (reaction, user) = await self.bot.wait_for(
                'reaction_add',
                check=lambda r, u: u.id == ctx.author.id and str(r) in ('✅', '❌'),
                timeout=15
            )

        if str(reaction) == '✅':
            await self.db.execute(
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
            self.bot.cache[str(ctx.guild.id)]['prefix'] = prefix
            await ctx.reply('changed the prefix for this guild. 👌')
        else:
            await ctx.send('Alright then. 👌')


def setup(bot):
    bot.add_cog(Meta(bot))
