import discord
from discord import Interaction
from discord.ext import commands


class Vagas(commands.Cog):
    """Comandos relacionados as vagas"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name='vagas')
    async def vagas(self, interaction: Interaction):
        await interaction.response.send_message("Tentanto ver as vagas pra vc!!!")


async def setup(bot):
    await bot.add_cog(Vagas(bot))
