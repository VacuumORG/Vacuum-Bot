import discord
from discord import Interaction
from discord.ext import commands
from reactionmenu import ViewMenu, ViewButton


class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_helper(self):
        help_text = """• /commands - Apresenta todos os comandos disponíveis para o seu cargo no servidor.
        """
        group_name = "Básico"
        return [group_name, help_text]

    @discord.app_commands.command(name='commands')
    async def commands(self, interaction: Interaction):
        helpers = [cog.get_helper() for cog in self.bot.cogs.values()]
        helpers_dict = dict(helpers)

        actual_helper = helpers[0]
        remaining_helpers = dict(helpers_dict)
        remaining_helpers.pop(actual_helper[0])

        menu = ViewMenu(interaction, menu_type=ViewMenu.TypeEmbed)
        empty_followup = ViewButton.Followup(details=ViewButton.Followup.set_caller_details(lambda: ...))
        menu.add_page(discord.Embed(title=f"Comandos {actual_helper[0]}", description=actual_helper[1],
                                    color=discord.Color.blurple()))
        buttons = [
            ViewButton(label=f'{helper_name}', custom_id=ViewButton.ID_CALLER, followup=empty_followup) for helper_name
            in remaining_helpers.keys()
        ]

        async def update_page(payload):
            button: ViewButton = payload.button
            actual_helper_name = button.label
            actual_helper_text = helpers_dict[actual_helper_name]

            remaining_helpers = dict(helpers_dict)
            remaining_helpers.pop(actual_helper_name)

            new_page = discord.Embed(title=f"Comandos {actual_helper_name}", description=actual_helper_text,
                                     color=discord.Color.blurple())
            new_buttons = [
                ViewButton(label=f'{helper_name}', custom_id=ViewButton.ID_CALLER, followup=empty_followup) for
                helper_name
                in remaining_helpers.keys()
            ]
            await menu.update(new_pages=[new_page], new_buttons=new_buttons)

        menu.add_buttons(buttons)
        menu.set_relay(update_page)
        await menu.start()


async def setup(bot):
    await bot.add_cog(Utils(bot))
