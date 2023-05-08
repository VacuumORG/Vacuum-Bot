import asyncio
import logging.handlers
from os import getenv

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Setting log
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='log/discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Setting env variables
load_dotenv()
token = getenv('TOKEN')
guild_id = getenv('GUILD_ID')

# Setting bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='/', intents=intents)
guild = discord.Object(id=guild_id)

extensions = [
    'cogs.admin',
    'cogs.vagas',
    'cogs.utils'
]


@bot.event
async def on_ready():
    print("bot is up")


async def setup_extensions():
    for extension in extensions:
        try:
            await bot.load_extension(extension)
        except Exception as e:
            print(f"Cannot load the extension {extension}. Exception:\n{e}")


async def setup_hook():
    bot.tree.clear_commands(guild=guild)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync()
    await bot.tree.sync(guild=guild)


bot.setup_hook = setup_hook

if __name__ == "__main__":
    asyncio.run(setup_extensions())
    bot.run(token, log_handler=None)
