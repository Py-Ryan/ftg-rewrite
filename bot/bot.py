import toml

from os import listdir, getcwd
from discord import Game
from datetime import datetime
from asyncpg import create_pool
from discord.ext import commands
from humanize import naturaldelta
from aiohttp import ClientSession


with open('bot/config.toml', 'r') as file:
    config = toml.load(file).get('credentials', None)

    if not {'token', 'db_url'} <= set(config):
        raise ValueError("TOML config file missing `token` and/or `db_url` keys.")


class Context(commands.Context):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def reply(self, content, **kwargs):
        """Kinda like discord.js user.reply."""
        return await self.send(f'{self.author.mention}, {content}', **kwargs)


class Ftg(commands.Bot):
    __slots__ = ("db_url", "token", "_raw_uptime", "db", "cache", "session")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache = {}
        self._raw_uptime = datetime.now()
        (self.db, self.session) = (None, None)

        for (attribute, value) in kwargs.items():
            setattr(self, attribute, value)

    @property
    def uptime(self):
        """Formatted bot uptime."""
        return naturaldelta(self._raw_uptime) if self._raw_uptime else None

    async def setup(self):
        (self.db, self.session) = (await create_pool(
            self.db_url,
            min_size=1,
            max_size=5,
        ), ClientSession())

    def run(self):
        """Connects the bot to discord & mounts the cogs."""
        for ext in self.modules:
            if not ext.startswith('__'):
                self.load_extension(f'cogs.{ext[:-3]}')
                print(f'Loaded {ext}.')

        self.loop.run_until_complete(self.setup())

        guilds = self.loop.run_until_complete(
            self.db.fetch(
                """
                SELECT (id, prefix)
                FROM guilds
                """
            )
        )

        for row in guilds:
            (guild_id, prefix) = row['row']
            self.cache[str(guild_id)] = {'prefix': prefix}

        for (name, obj) in self.cogs.items():
            with open(f'./cogs/{name.lower()}.py', encoding='utf8') as extension:
                obj.loc = len(extension.readlines())
                obj.db = self.db
                obj._raw_uptime = datetime.now()

        self.load_extension("jishaku")
        super().run(self.token)

    async def on_ready(self):
        if self._raw_uptime <= datetime.utcnow():
            print(f'{self.user} is ready.')

    async def on_message(self, message):
        if self.is_ready():
            context = await self.get_context(message, cls=Context)
            await self.invoke(context)

    async def on_command_error(self, context, exception):
        exception = getattr(exception, 'original', exception)

        if not isinstance(exception, (commands.CommandOnCooldown, commands.CommandNotFound)):
            raise exception


def get_prefix(bot, message):
    if message.guild is not None:
        guild = bot.cache.setdefault(str(message.guild.id), {'prefix': 'gn '})
        return commands.when_mentioned_or(guild["prefix"])(bot, message)
    else:
        return commands.when_mentioned_or('gn ')(bot, message)


ftg = Ftg(
    **config,
    modules=listdir('./cogs'),
    command_prefix=get_prefix,
    activity=Game('default prefix is a mention')
)

if __name__ == '__main__':
    ftg.run()
