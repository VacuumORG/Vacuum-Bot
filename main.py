import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from os import getenv
from jobs.programathor import get_link_jobs

load_dotenv()
token =getenv('TOKEN')

bot  = commands.Bot(command_prefix="/",intents= discord.Intents.all())

string_name =''.join(get_link_jobs())

@bot.event
async def on_ready():
    print("bot is up")
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name='vagas')
async def vagas(interaction: discord.integrations):
    await interaction.response.send_message(string_name)

@bot.tree.command(name="say")
@app_commands.describe(thing_to_say = "What should I say?")
async def say(interaction: discord.Interaction, thing_to_say: str):
  await interaction.response.send_message(f"{interaction.user.name} said: `{thing_to_say}`")

bot.run(token)
