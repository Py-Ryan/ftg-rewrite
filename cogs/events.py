from datetime import datetime
from discord.ext import commands
from aiohttp import MultipartWriter
from collections import deque, namedtuple

class Events(commands.Cog):
    """Cog that'll handle exlusively events."""

    deque_message = namedtuple('deque_message', ['content', 'author', 'when', 'channel', 'attachments'])

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            channel = self.bot.cache[str(message.guild.id)][str(message.channel.id)]['messages']['deleted']

            channel.appendleft(
                    type(self).deque_message(
                    content=message.content,
                    author=message.author.id,
                    when=datetime.now(),
                    channel=message.channel.name,
                    attachments=message.attachments
                )
            )

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.author.bot:
            channel = self.bot.cache[str(after.guild.id)][str(after.channel.id)]['messages']['edited']

            channel.appendleft(
                    type(self).deque_message(
                    content={'b': before.content, 'a': after.content},
                    author=after.author.id,
                    when=datetime.now(),
                    channel=after.channel.name,
                    attachments=after.attachments
                )
            )


def setup(bot):
    bot.add_cog(Events(bot))
