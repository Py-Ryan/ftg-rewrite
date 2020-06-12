from datetime import datetime
from discord.ext import commands
from collections import deque, namedtuple


class Events(commands.Cog):
    """Cog that'll handle exlusively events."""

    deleted_message = namedtuple('deleted_message', ['content', 'author', 'when', 'channel', 'attachments'])

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        guild = self.bot.cache.setdefault(str(message.guild.id), {'messages': {'deleted': deque()}})

        if not guild.get('messages', None):
            guild['messages'] = {'deleted': deque()}

        guild['messages']['deleted'].appendleft(
            type(self).deleted_message(
                content=message.content,
                author=message.author.id,
                when=datetime.now(),
                channel=message.channel.name,
                attachments=message.attachments
            )
        )


def setup(bot):
    bot.add_cog(Events(bot))
