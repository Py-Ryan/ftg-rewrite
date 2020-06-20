from random import randint
from contextlib import suppress
from humanize import naturaltime
from discord.ext import commands
from typing import Union, Optional
from .utils.dispatchers import _info_embed_builder
from discord import User, Embed, Member, Status, Colour, HTTPException, ClientUser


class BetterUserConverter(commands.Converter):
    """A user converter that supports fetching users out of the global user cache."""

    async def convert(self, ctx, argument):
        result = None
        try:
            converter = commands.UserConverter()
            result = await converter.convert(ctx, argument)
        except commands.BadArgument:
            with suppress(HTTPException, ValueError):
                result = await ctx.bot.fetch_user(int(argument))
        finally:
            return result


class Meta(commands.Cog):
    """Cog used for general commands that don't belong anywhere specific."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def info(self, ctx, *, user: Union[Member, BetterUserConverter, str] = None):
        user  = user or self.bot.user
        embed = _info_embed_builder(ctx, user)
        await ctx.send(embed=embed)

    @info.command(name='cog')
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def info_cog(self, ctx, *, cog='Fun'):
        cogs = self.bot.cogs
        cog  = cogs.get(cog.capitalize()) or cogs['Meta']

        loc       = cog.loc
        avatar    = str(self.bot.user.avatar_url_as(static_format='png'))
        uptime    = naturaltime(cog._raw_uptime)
        cog_name  = type(cog).__name__.lower()
        cmd_count = len(cog.get_commands())
        info_desc = f'Information on the {cog_name} extension.'

        info = (
            Embed(title=cog_name.capitalize(), description=info_desc, colour=randint(0, 0xffffff))
            .add_field(name='**Command Count**', value=cmd_count, inline=True)
            .add_field(name='**Lines Of Code**', value=loc, inline=True)
            .set_footer(text=f'Extension loaded {uptime}.')
            .set_thumbnail(url=avatar)
        )

        await ctx.send(embed=info)

    @commands.command(aliases=['avatar', 'pfp'])
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def av(self, ctx, *, user: Union[BetterUserConverter, str] = None):
        user   = ctx.author if user == 'me' or not user else user
        avatar = str(user.avatar_url_as(static_format='png'))

        embed = Embed(title=f"{user}'s avatar:", url=avatar, colour=randint(0, 0xffffff))
        embed.set_image(url=avatar)

        message = await ctx.send(embed=embed)
        await message.add_reaction('\u23f9')

        with suppress(TimeoutError):
            check = lambda r, u: (
                u is user or
                r.message.channel.permissions_for(u).manage_messages or
                u.id == 700091773695033505
            )
            (reaction, user) = await self.bot.wait_for('reaction_add', check=check, timeout=900)

        if str(reaction) == '\u23f9':
            await message.delete()

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
