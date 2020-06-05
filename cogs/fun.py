from discord import Embed
from random import randint
from discord.ext import commands
from string import ascii_letters as alphabet_


class FunCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def binary(self, ctx, *, text):
        """Convert text to binary or vise versa. Enter binary bytes separated by spaces to convert into utf-8."""
        try:
            output = ''.join([chr(int(byte, 2)) for byte in text.split()])
        except ValueError:
            output = ' '.join([bin(ord(char))[2:].zfill(8) for char in text])

        async with self.bot.session.post('https://hastebin.com/documents', data=output) as post:
            data = await post.json()

            url_code = data.get('key', None)
            if url_code:
                await ctx.send(
                    f'{ctx.author.mention}, https://hastebin.com/{url_code}')

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def caesar(self, ctx, *, text):
        """Convert plain text into a caesar cipher. Default shift factor is 4."""
        table = str.maketrans(alphabet_, alphabet_[4:] + alphabet_[:4])
        await ctx.send(f"{ctx.author.mention}, *{text.translate(table)}*")

    @commands.command()
    @commands.cooldown(1, 0.75, commands.BucketType.guild)
    async def catfact(self, ctx):
        async with self.bot.session.get("https://catfact.ninja/fact?max_length=100") as g:
            embed = Embed(description=(await g.json())["fact"], colour=randint(0, 0xffffff))
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(FunCog(bot))
