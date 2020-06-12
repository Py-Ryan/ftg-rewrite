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
        if message.author.bot:
            return

        guild = self.bot.cache[str(message.guild.id)]

        guild['messages']['deleted'].appendleft(
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
        if after.author.bot:
            return

        guild = self.bot.cache[str(after.guild.id)]

        if before.content != after.content:
            guild['messages']['edited'].appendleft(
                type(self).deque_message(
                    content={'before': before.content, 'after': after.content},
                    author=after.author.id,
                    when=datetime.now(),
                    channel=after.channel.name,
                    attachments=after.attachments
                )
            )


def setup(bot):
    bot.add_cog(Events(bot))
