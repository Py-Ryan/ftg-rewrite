import discord
from humanize import naturaltime
from discord.ext import commands
from multipledispatch import dispatch

status_cases = {
    discord.Status.online: discord.Colour.green(),
    discord.Status.idle: discord.Colour.orange(),
    discord.Status.dnd: discord.Colour.red(),
    discord.Status.offline: discord.Colour.light_grey()
}

@dispatch(commands.Context, discord.Member)
def _info_embed_builder(ctx, member):
    uid      = member.id
    desc     = f'[Avatar URL]({member.avatar_url})'
    joined   = naturaltime(member.joined_at)
    avatar   = member.avatar_url_as(static_format='png')
    colour   = status_cases[member.status]
    created  = naturaltime(member.created_at)
    top_role = str(member.top_role)

    embed = (
        discord.Embed(
            title=str(member),
            description=desc,
            colour=colour
        )
        .add_field(name='**Account Created**', value=created, inline=False)
        .add_field(name='**Joined**', value=joined, inline=False)
        .add_field(name='**Discord ID**', value=uid, inline=False)
        .add_field(name='**Top Role**', value=top_role, inline=False)
        .set_thumbnail(url=avatar)
    )

    return embed

@dispatch(commands.Context, discord.User)
def _info_embed_builder(ctx, user):
    uid     = user.id
    desc    = f'[Avatar URL]({user.avatar_url})'
    avatar  = user.avatar_url_as(static_format='png')
    colour  = discord.Colour.light_grey()
    created = naturaltime(user.created_at)

    embed = (
        discord.Embed(
            title=str(user),
            description=desc,
            colour=colour
        )
        .add_field(name='**Account Created**', value=created, inline=False)
        .add_field(name='**Discord ID**', value=uid, inline=False)
        .set_thumbnail(url=avatar)
    )

    if not ctx.guild:
        embed.set_footer(text='This user is not in this guild.')

    return embed

@dispatch(commands.Context, discord.ClientUser)
def _info_embed_builder(ctx, user):
    version = ctx.bot.__version__
    latency = round(ctx.bot.latency * 1000)
    embed   = _info_embed_builder(ctx, ctx.guild.me)

    embed.description = f'[Source Code](https://github.com/Py-Ryan/ftg-rewrite)'
    embed.add_field(name='**Uptime**', value=ctx.bot.uptime, inline=False)
    embed.add_field(name='**Latency**', value=f'{latency}ms', inline=False)
    embed.set_footer(text=f'Developer: well in that case#0082 (700091773695033505) | Version: {version}')

    return embed
