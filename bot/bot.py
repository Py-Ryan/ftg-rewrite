import ssl
import toml
from discord import Game
from os import listdir, path
from collections import deque
from datetime import datetime
from asyncpg import create_pool
from discord.ext import commands
from aiohttp import ClientSession

with open('config.toml', 'r') as file:
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
    __slots__ = ("_extensions", "_db_url", "_token", "_raw_uptime", "db", "cache", "session")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._extensions = kwargs.pop('extensions', [])
        self.api = {'ip': kwargs.pop('ip_key', None)}
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
        if not self._extensions or not isinstance(self._extensions, (tuple, list, set)):
            raise RuntimeWarning(
                f"Invalid type passed to {type(self).__name__}._extensions. Must be one of tuple, list, or set. "
                "Extensions will not be loaded")
        else:
            for cog in self._extensions:
                yield path.splitext(cog)

    async def setup(self):
        (self.db, self.session) = (await create_pool(
            self._db_url,
            min_size=1,
            max_size=5,
        ), ClientSession())

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

        for (name, obj) in self.cogs.items():
            with open(f'../cogs/{name}.py', encoding='utf8') as extension:
                obj.loc = len(extension.readlines())
                obj.db = self.db
                obj._raw_uptime = datetime.now()

        self.load_extension("jishaku")
        super().run(self._token)

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
        guild = bot.cache.setdefault(
            str(message.guild.id),
            {'prefix': 'gn ', 'messages': {'deleted': deque(), 'edited': deque()}}
        )
        return commands.when_mentioned_or(guild["prefix"])(bot, message)
    else:
        return commands.when_mentioned_or('gn ')(bot, message)


ftg = Ftg(
    **config,
    extensions=listdir('../cogs'),
    command_prefix=get_prefix,
    activity=Game('default prefix is mention')
)
ftg.run()
