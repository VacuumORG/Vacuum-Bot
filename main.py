import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
from os import getenv
from jobs.programathor import thor_jobs
from discord import Embed
from discord.ui import Button,View
from jobs.linkedin import linkedin_jobs

load_dotenv()
token =getenv('TOKEN')

bot  = commands.Bot(command_prefix="/",intents= discord.Intents.all())

def format_dict_list(dict_list):
    return "\n".join(f"{key}: {value}" for d in dict_list for key, value in d.items())

@bot.event
async def on_ready():
    print("bot is up")
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name='vagas')
async def vagas(interaction: discord.Interaction, programathor: str):
    # linked = linkedin_jobs(search=linkedin,cd=True)
    # resultado = []
    # for job in linked :
    #     resultado.append(f'\nJob: {job["Job"]}:{job["Apply"]}')
    #     resultt = "\n".join(resultado)
    thor=  thor_jobs(search=programathor)
    output= []
    for job in thor:
        techs_str = ", ".join(job["techs"])

        output.append(f'\nJob: {job["name"]}\nApply: {job["link"]}\nTechs: {techs_str}')

    result = "\n".join(output)

    await interaction.response.send_message(content=result,ephemeral = True, suppress_embeds = True )

bot.run(token)

