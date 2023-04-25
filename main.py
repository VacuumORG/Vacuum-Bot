import discord
from discord.ext import commands
from dotenv import load_dotenv
from os import getenv
from jobs.Sites import Sites

sites = Sites

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
    # linked = sites.linkedin_jobs(search=linkedin,cd=True)
    # resultado = []
    # for job in linked :
    #     resultado.append(f'\nJob: {job["Job"]}:{job["Apply"]}')
    #     resultt = "\n".join(resultado)

    thor = format_dict_list(sites.thor_jobs(search=programathor))


    await interaction.response.send_message(content=thor, ephemeral = True, suppress_embeds = True )

bot.run(token)

