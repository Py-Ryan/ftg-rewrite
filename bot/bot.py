import toml
import asyncio

from os import listdir
from random import randint
from collections import deque
from datetime import datetime
from asyncpg import create_pool
from discord import Game, Embed
from discord.ext import commands
from humanize import naturaldelta
from aiohttp import ClientSession
from traceback import format_exception

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

class MessageCache(deque):
    """Cache for deleted and edited messages."""

    def __init__(self, *args, **kwargs):
        self.maxsize = kwargs.pop('maxsize', 128)
        super().__init__(*args, **kwargs)

    def appendleft(self, *args):
        if len(self) >= self.maxsize:
            del self[-1]
        super().appendleft(*args)

class Ftg(commands.Bot):
    __slots__ = ('db_url', 'token', '_raw_uptime', 'db', 'cache', 'session')

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

    async def finish(self):
        """Close the bot and release the aiohttp session."""
        await self.db.close()
        await self.session.close()
        await super().logout()

    async def start(self):
        """Connects the bot to discord & mounts the cogs."""
        for ext in self.modules:
            if not ext.startswith('__'):
                self.load_extension(f'cogs.{ext[:-3]}')
                print(f'Loaded {ext}.')

        (self.db, self.session) = (await create_pool(
            self.db_url,
            min_size=1,
            max_size=5,
        ), ClientSession())

        async with self.session.get('https://raw.githubusercontent.com/Py-Ryan/ftg-rewrite/master/readme.md') as get:
            self.__version__ = (await get.text()).split("\n")[4]

        guilds = await self.db.fetch(
            """
            SELECT (id, prefix)
            FROM guilds
            """
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
        await super().start(self.token)

    async def on_ready(self):
        if self._raw_uptime <= datetime.utcnow():
            print(f'{self.user} is ready.')

    async def on_message(self, message):
        if self.is_ready():
            try:
                guild = self.cache.setdefault(str(message.guild.id), {'prefix': 'gn '})
                channel = guild.setdefault(str(message.channel.id), {'messages': {'deleted': MessageCache(), 'edited': MessageCache()}})
            except AttributeError:
                pass

            context = await self.get_context(message, cls=Context)
            await self.invoke(context)

    async def on_command_error(self, context, exception):
        exception = getattr(exception, 'original', exception)

        if not isinstance(exception, (commands.CommandNotFound, commands.CommandOnCooldown)):
            tb = '\n'.join(format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))

            async with self.session.post('https://haste.crrapi.xyz/documents', data=tb) as post:
                key = (await post.json()).get('key', None)
                tb = f'https://haste.crrapi.xyz/{key}' if key else None

            embed = (
                Embed(
                    title='Unhandled Exception \❌',
                    colour=randint(0, 0xffffff),
                    description=f'[Traceback]({tb})\n```{exception}```' if tb else '```Unknown traceback.```'
                )
                .add_field(name='**Command**', value=context.command.qualified_name, inline=True)
                .add_field(name='**Author**', value=context.author.id, inline=True)
                .set_thumbnail(url=str(self.user.avatar_url_as(static_format='png')))
            )

            await context.message.add_reaction('❌')
            await self.get_channel(self.debug_channel_id).send(embed=embed)
            await context.send("There's been an unexpected error. A report has been generated. Will soon be fixed :-)")

def get_prefix(bot, message):
    try:
        prefix = bot.cache.get(str(message.guild.id), {'prefix': 'gn '})['prefix']
        return commands.when_mentioned_or(prefix)(bot, message)
    except AttributeError:
        return commands.when_mentioned_or('gn ')(bot, message)


ftg = Ftg(
    **config,
    modules=listdir('./cogs'),
    command_prefix=get_prefix,
    activity=Game('default prefix is a mention')
)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(ftg.start())
    except KeyboardInterrupt:
        loop.run_until_complete(ftg.finish())
