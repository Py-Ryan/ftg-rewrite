from contextlib import suppress
from discord.ext import commands
from asyncio import TimeoutError


class ConfigCog(commands.Cog):
    """Cog used for configuration commands for guilds & users."""

    def __init__(self, bot):
        self.bot = bot

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
    bot.add_cog(ConfigCog(bot))
