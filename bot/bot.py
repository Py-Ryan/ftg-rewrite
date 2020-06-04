import toml

from os import listdir, path
from datetime import datetime
from asyncpg import create_pool
from discord.ext import commands

with open('config.toml', 'r') as file:
    config = toml.load(file)
    config = config.get('credentials', None)


class Ftg(commands.Bot):
    __slots__ = ("_extensions", "_db_url", "_token", "_raw_uptime", "db", "cache")

    def __init__(self, **kwargs):
        super().__init__(command_prefix=kwargs.pop('command_prefix', self.prefix_getter), **kwargs)
        self._extensions = kwargs.pop('extensions', None)
        self._db_url = kwargs.pop('db_url', None)
        self._token = kwargs.pop('token', None)
        self._raw_uptime = datetime.utcnow()
        self.cache = {}
        self.run()
        self.db = self.loop.run_until_complete(create_pool(self._db_url))

    @property
    def uptime(self):
        """Formatted bot uptime."""
        return self._raw_uptime.strftime('%H:%M:%S') if self._raw_uptime else None

    @property
    def extensions(self):
        """Generator yielding the a (filename, extension) tuple of the extensions."""
        for cog in self._extensions:
            yield path.splitext(cog)

    def prefix_getter(self, bot, message):
        prefix = self.cache.setdefault(str(message.guild.id), {}).setdefault("prefix", 'suddy ')
        print(self.cache)
        return commands.when_mentioned_or(prefix)(bot, message)

    def run(self):
        """Connects the bot to discord & mounts the cogs."""
        for base, ext in self.extensions:
            if ext == '.py' and not base.startswith('__'):
                self.load_extension(f'cogs.{base}')
                print(f'Loaded {base}.')
        self.load_extension("jishaku")

        super().run(self._token)

    def add_cog(self, cog):
        cog.__dict__.setdefault('_raw_uptime', datetime.utcnow())
        super().add_cog(cog)

    async def on_ready(self):
        if self._raw_uptime <= datetime.utcnow():
            print(f'{self.user} is ready.')


suddy = Suddy(token=config.get('token', None), extensions=listdir('../cogs'))
