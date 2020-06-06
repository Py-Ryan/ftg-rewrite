import re
from random import randint
from discord.ext import commands
from discord import Embed, AllowedMentions
from textwrap import wrap as insert_spaces
from string import ascii_letters as alphabet_


class FunCog(commands.Cog):
    """Cog used for fun commands."""

    def __init__(self, bot):
        self.bot = bot

    binary_regex = re.compile(r'^[0-1]{8}$')
    ip_regex = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

    @commands.command()
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def binary(self, ctx, *, text):
        """Convert text to binary or vise versa. Enter binary bytes separated by spaces to convert into ASCII."""
        try:
            binary = insert_spaces(text.strip(), 8)
            if all(re.match(type(self).binary_regex, b) for b in binary) and len(text) % 8:
                output = ''.join([chr(int(byte, 2)) for byte in binary])
            else:
                raise ValueError
        except ValueError:
            output = ' '.join([bin(ord(char))[2:].zfill(8) for char in text])

        if len(output) >= 150:
            async with self.bot.session.post('https://haste.crrapi.xyz/documents', data=output) as post:
                url_code = (await post.json()).get('key', None)
                if url_code:
                    await ctx.send(f'{ctx.author.mention}, https://haste.crrapi.xyz/raw/{url_code}')
        else:
            await ctx.send(f'{ctx.author.mention}, {output}',
                           allowed_mentions=AllowedMentions(everyone=False, roles=False))

    @commands.command()
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def caesar(self, ctx, *, text):
        """Convert plain text into a caesar cipher. Default shift factor is 4."""
        table = str.maketrans(alphabet_, alphabet_[4:] + alphabet_[:4])
        await ctx.send(f'{ctx.author.mention}, {text.translate(table)}')

    @commands.command()
    @commands.cooldown(1, 0.75, commands.BucketType.guild)
    async def catfact(self, ctx):
        """Random cat facts. UwU."""
        async with self.bot.session.get('https://catfact.ninja/fact?max_length=100') as g:
            embed = Embed(description=(await g.json())['fact'], colour=randint(0, 0xffffff))
            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def ip(self, ctx, *, ip):
        ip = re.search(type(self).ip_regex, ip)
        try:
            string = f'https://api.ipgeolocation.io/ipgeo?apiKey={self.bot.api["ip"]}&ip={ip.string}'
            async with self.bot.session.get(string) as g:
                info = await g.json()

            embed = (
                Embed(title=ip.string, colour=randint(0, 0xffffff))
                .add_field(name='**Continent:**', value=info['continent_name'], inline=True)
                .add_field(name='**Country:**', value=info['country_name'], inline=True)
                .add_field(name='**State/Province:**', value=info['state_prov'], inline=False)
                .add_field(name='**City:**', value=info['city'], inline=True)
                .add_field(name='**Zip:**', value=info['zipcode'], inline=False)
                .set_footer(
                    text=f'Calling Code: {info["calling_code"]} | Lat: {info["latitude"]} | Long: {info["longitude"]}'
                )
                .set_thumbnail(url=info['country_flag'])
            )

            await ctx.send(embed=embed)
        except (AttributeError, KeyError):
            await ctx.send(f'{ctx.author.mention}, Invalid IP.')


def setup(bot):
    bot.add_cog(FunCog(bot))
