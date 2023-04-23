import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from os import getenv
from jobs.programathor import i
from discord import Embed
from discord.ui import Button,View
from jobs.linkedin import get_job_links

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

@bot.tree.command(name='vags')
async def vags(interaction: discord.integrations):
    linked = format_dict_list(get_job_links(search='junior',cd= True))
    # thor=  i(search=programathor)
    # output= []
    # for job in thor:
    #     techs_str = ", ".join(job["techs"])

    #     output.append(f'\nJob: {job["name"]}\nApply: {job["link"]}\nTechs: {techs_str}')

    # result = "\n".join(output)

    # await interaction.response.send_message(result,ephemeral= True, suppress_embeds= True )

    await interaction.response.send_message(linked,ephemeral= True, suppress_embeds= True )


bot.run(token)


