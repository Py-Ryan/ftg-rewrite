import re

from random import randint
from discord.ext import commands
from collections import defaultdict
from discord import Embed, AllowedMentions
from textwrap import wrap as insert_spaces
from string import ascii_letters as alphabet_


class Fun(commands.Cog):
    """Cog used for fun commands."""

    def __init__(self, bot):
        self.bot = bot

    binary_regex = re.compile(r'^[0-1]{8}$')
    ip_regex = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

    async def _haste_helper(self, ctx, output):
        """Helper function that posts long outputs of conversion commands to a haste server."""
        if len(output) >= 200:
            async with self.bot.session.post('https://haste.crrapi.xyz/documents', data=output) as post:
                url_code = (await post.json()).get('key', None)
                if url_code:
                    await ctx.reply(f'https://haste.crrapi.xyz/raw/{url_code}')
        else:
            await ctx.reply(output, allowed_mentions=AllowedMentions(everyone=False, roles=False, users=False))

    @staticmethod
    async def _attachment_helper(ctx):
        output = ''
        attachments = ctx.message.attachments

        if attachments:
            for attachment in attachments:
                try:
                    output += ''.join((await attachment.read()).decode('utf-8').replace(' ', '\n'))
                except UnicodeDecodeError:
                    return await ctx.reply('use text files.')

        return output

    @commands.command()
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def binary(self, ctx, *, text=''):
        """Convert text to binary or vise versa."""
        text = await type(self)._attachment_helper(ctx) or text

        try:
            binary = insert_spaces(text.strip(), 8)
            if len(text) % 8 and all(re.match(type(self).binary_regex, b) for b in binary):
                output = ''.join([chr(int(byte, 2)) for byte in binary]).replace('\n', ' ')
            else:
                raise ValueError
        except ValueError:
            output = ' '.join([bin(ord(char))[2:].zfill(8) for char in text])

        await self._haste_helper(ctx, output)

    @commands.command(name='hex')
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def _hex(self, ctx, *, text=''):
        """Convert text to hexadecimal or vice versa."""
        text = await type(self)._attachment_helper(ctx) or text

        try:
            output = bytes.fromhex(text).decode('utf-8')
        except ValueError:
            output = ''.join([str(hex(ord(char)))[2:] for char in text])

        await self._haste_helper(ctx, output)

    @commands.command()
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def morse(self, ctx, *, text=''):
        """Convert text into morse code and vice versa."""
        text = await type(self)._attachment_helper(ctx) or text
        operator = 'decode' if {'.', '-', ' '}.issuperset(text) else 'encode'

        async with self.bot.session.get(f'http://www.morsecode-api.de/{operator}?string={text}') as get:
            key = 'morsecode' if operator == 'encode' else 'plaintext'
            output = (await get.json()).get(key, None)

        if len(output) <= 1:
            await ctx.reply('invalid morse code.')
        else:
            await self._haste_helper(ctx, output)

    @commands.command()
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def caesar(self, ctx, *, text):
        """Convert plain text into a caesar cipher. Default shift factor is 4."""
        table = str.maketrans(alphabet_, alphabet_[4:] + alphabet_[:4])
        await ctx.reply(text.translate(table))

    @commands.command()
    @commands.cooldown(1, 0.75, commands.BucketType.guild)
    async def catfact(self, ctx):
        """Random cat facts. UwU."""
        async with self.bot.session.get('https://catfact.ninja/fact?max_length=100') as g:
            embed = Embed(description=(await g.json()).get('fact', None), colour=randint(0, 0xffffff))
            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 1.5, commands.BucketType.guild)
    async def ip(self, ctx, *, ip):
        """Get information regarding a specific IP address."""
        ip = re.search(type(self).ip_regex, ip)
        string = f'https://api.ipgeolocation.io/ipgeo?apiKey={self.bot.ip_key}&ip={ip.string}'

        async with self.bot.session.get(string) as g:
            info = await g.json() or defaultdict(lambda: 'None')

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


def setup(bot):
    bot.add_cog(Fun(bot))
