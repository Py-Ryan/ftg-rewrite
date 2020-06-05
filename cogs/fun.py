import random
from discord.ext import commands
from string import ascii_letters as alphabet_


class FunCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
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
                    f'{ctx.author.mention}, **here is your converted text!\nhttps://hastebin.com/{url_code}**')
            else:
                raise RuntimeError(f'Failed to upload text to hastebin: {data.get("message", None)}')

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def caesar(self, ctx, *, text):
        """Convert plain text into a caesar cipher. Default shift factor is 4."""
        shifted = alphabet_[4:] + alphabet_[:4]
        table = str.maketrans(alphabet_, shifted)
        await ctx.send(f"{ctx.author.mention}, *{text.translate(table)}*")

    @caesar.command(name='swap')
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def caesar_simple(self, ctx, * text):
        output = ""
        for character in text:
            char = random.choice(text)
            if output.count(char) <= text.count(char):
                output += char

        await ctx.send(f'{ctx.author.mention}, **here you are**:\n*{output}*')


def setup(bot):
    bot.add_cog(FunCog(bot))
