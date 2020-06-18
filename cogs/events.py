from datetime import datetime
from discord.ext import commands
from collections import deque, namedtuple


class Events(commands.Cog):
    """Cog that'll handle exlusively events."""

    deque_message = namedtuple('deque_message', ['content', 'author', 'when', 'channel', 'attachments'])

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            guild   = str(message.guild.id)
            channel = str(message.channel.id)
            entry   = self.bot.cache[guild][channel]['messages']['deleted']

            entry.appendleft(
                    type(self).deque_message(
                    when=datetime.now(),
                    content=message.content,
                    channel=message.channel.name,
                    author=str(message.author.id),
                    attachments=message.attachments
                )
            )

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.author.bot:
            guild   = str(before.guild.id)
            channel = str(before.channel.id)
            entry   = self.bot.cache[guild][channel]['messages']['edited']

            entry.appendleft(
                    type(self).deque_message(
                    when=datetime.now(),
                    channel=after.channel.name,
                    author=str(before.author.id),
                    attachments=after.attachments,
                    content={'b': before.content, 'a': after.content}
                )
            )


def setup(bot):
    bot.add_cog(Events(bot))
