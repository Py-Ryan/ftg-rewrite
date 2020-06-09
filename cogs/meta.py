from typing import Union
from random import randint
from contextlib import suppress
from humanize import naturaltime
from discord.ext import commands
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
            github = "https://raw.githubusercontent.com/Py-Ryan/ftg-rewrite/master/README.md"
            async with self.bot.session.get(github) as get:
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
            await ctx.reply("couldn't find a user with that identification.")
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
        message = await ctx.reply(f'change the guild prefix to `{prefix}`?')

        for reaction in ('✅', '❌'):
            await message.add_reaction(reaction)

        with suppress(TimeoutError):
            (reaction, user) = await self.bot.wait_for(
                'reaction_add',
                check=lambda r, u: u.id == ctx.author.id and str(r) in ('✅', '❌'),
                timeout=15
            )

        if str(reaction) == '\U00002705':
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

    @info.command(name='cog')
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def info_cog(self, ctx, *, cog='Fun'):
        cog = cog.capitalize()
        cogs = self.bot.cogs
        info_cog = cogs.get(cog, None)

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


def setup(bot):
    bot.add_cog(Meta(bot))
