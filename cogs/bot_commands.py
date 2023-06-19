import discord
from discord import Interaction
from discord.ext import commands

from shared.view_menu import ViewMenu


class BotCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name='comandos')
    async def _commands(self, interaction: Interaction):
        hasHelper = lambda x: hasattr(x, 'get_helper') and callable(getattr(x, 'get_helper'))
        helpers = [cog.get_helper() for cog in self.bot.cogs.values() if hasHelper(cog)]

        menu = ViewMenu(interaction, pages=helpers)
        await menu.start()


async def setup(bot):
    await bot.add_cog(BotCommands(bot))
