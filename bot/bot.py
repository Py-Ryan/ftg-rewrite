import toml

from os import listdir, path
from collections import deque
from datetime import datetime
from asyncpg import create_pool
from discord.ext import commands
from aiohttp import ClientSession


with open('config.toml', 'r') as file:
    config = toml.load(file)
    config = config.get('credentials', None)


class Ftg(commands.Bot):
    __slots__ = ("_extensions", "_db_url", "_token", "_raw_uptime", "db", "cache", "session")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._extensions = kwargs.pop('extensions', [])
        self._db_url = kwargs.pop('db_url', None)
        self._token = kwargs.pop('token', None)
        self._raw_uptime = datetime.utcnow()
        self.session = None
        self.cache = {}
        self.db = None

    @property
    def uptime(self):
        """Formatted bot uptime."""
        return self._raw_uptime.strftime('%H:%M:%S') if self._raw_uptime else None

    @property
    def extensions(self):
        """Generator yielding the a (filename, extension) tuple of the extensions."""
        if not self._extensions:
            yield None
        else:
            for cog in self._extensions:
                yield path.splitext(cog)

    async def setup(self):
        self.db = await create_pool(self._db_url, min_size=1, max_size=5)
        self.session = ClientSession()

    def run(self):
        """Connects the bot to discord & mounts the cogs."""
        for base, ext in self.extensions:
            if ext == '.py' and not base.startswith('__'):
                self.load_extension(f'cogs.{base}')
                print(f'Loaded {base}.')

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
            self.cache[str(guild_id)] = {'prefix': prefix, 'messages': {'deleted': deque(), 'edited': deque()}}

        self.load_extension("jishaku")
        super().run(self._token)

    def add_cog(self, cog):
        cog.__dict__.setdefault('_raw_uptime', datetime.utcnow())
        super().add_cog(cog)

    async def on_ready(self):
        if self._raw_uptime <= datetime.utcnow():
            print(f'{self.user} is ready.')


def get_prefix(bot, message):
    guild = bot.cache.setdefault(
        str(message.guild.id),
        {'prefix': 'gn ', 'messages': {'deleted': deque(), 'edited': deque()}}
    )

    return commands.when_mentioned_or(guild["prefix"])(bot, message)


ftg = Ftg(
    token=config.get('token', None),
    extensions=listdir('../cogs'),
    command_prefix=get_prefix,
    db_url=config.get('db_url', None)
)
ftg.run()
