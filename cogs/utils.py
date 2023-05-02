import discord
from discord import Interaction
from discord.ext import commands
from reactionmenu import ViewMenu, ViewButton


class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name='commands')
    async def commands(self, interaction: Interaction):
        menu = ViewMenu(interaction, menu_type=ViewMenu.TypeEmbed)
        menu.add_page(discord.Embed(title="Comandos do Vacuum Bot", description="Os comandos do bot!",
                                    color=discord.Color.blurple()))

        buttons = []

        async def update_page(payload):
            button: ViewButton = payload.button
            page_name = button.name
            pages = {
                "vagas": discord.Embed(title="Comandos Vagas", description="/vagas"),
                "utils": discord.Embed(title="Comandos Utils", description="/commands")
            }
            page = pages[page_name]
            await menu.update(new_pages=[page], new_buttons=buttons)

        empty_followup = ViewButton.Followup(details=ViewButton.Followup.set_caller_details(lambda: ...))
        page_1_button = ViewButton(label='Vagas', name="vagas", custom_id=ViewButton.ID_CALLER, followup=empty_followup)
        page_2_button = ViewButton(label='Utils', name="utils", custom_id=ViewButton.ID_CALLER, followup=empty_followup)

        buttons.extend([page_1_button, page_2_button])

        menu.add_buttons(buttons)
        menu.set_relay(update_page)
        await menu.start()


async def setup(bot):
    await bot.add_cog(Utils(bot))
