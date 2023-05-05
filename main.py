import asyncio
from os import getenv

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = getenv('TOKEN')
guild_id = getenv('GUILD_ID')

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


def format_dict_list(dict_list):
    return "\n".join(f"{key}: {value}" for d in dict_list for key, value in d.items())


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
    bot.run(token)
