import typing
import discord
from typing import Optional, Literal
from discord import Interaction
from discord.ext import commands
from reactionmenu import ViewMenu, ViewButton

from tools import chunks
from jobs.Sites import Sites

SENIORITY_LEVELS = Literal['Júnior', 'Pleno', 'Sênior']
JOBS_PER_PAGE = 10


def build_jobs_page(title, jobs):
    description = "\n".join([f"[{job['Job']}]({job['Apply']})" for job in jobs])
    return discord.Embed(title=title, description=description)


class Vagas(commands.Cog):
    """Comandos relacionados as vagas"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sites = Sites()

    async def scrap_and_update_menu_with_jobs(self, seniority: SENIORITY_LEVELS, menu):
        linkedin_jobs = await self.sites.linkedin_jobs(seniority, True)
        nerdin_jobs = await self.sites.nerdin_jobs(seniority)
        thor_jobs = await self.sites.thor_jobs(seniority)
        jobs = [*linkedin_jobs, *nerdin_jobs, *thor_jobs]
        chunked_jobs = chunks(jobs, JOBS_PER_PAGE)

        pages_title = f"Mostrando vagas de {seniority}"
        pages = [build_jobs_page(pages_title, page_jobs) for page_jobs in chunked_jobs]
        await menu.update(new_pages=pages, new_buttons=[ViewButton.back(), ViewButton.next(), ViewButton.end_session()])

    @discord.app_commands.command(name='vagas')
    @discord.app_commands.rename(seniority='senioridade')
    @discord.app_commands.describe(seniority="Escolha a senioridade da vaga.")
    async def vagas(self, interaction: Interaction, seniority: Optional[SENIORITY_LEVELS] = None):
        """Pesquise por vagas utilizando nosso bot."""
        menu = ViewMenu(interaction, menu_type=ViewMenu.TypeEmbed, timeout=180)

        if seniority:
            menu.add_page(discord.Embed(title="Vacuum Vagas",
                                        description=f"Segura um tico ai campeão, estou buscando as vagas de {seniority} ..."))
            menu.add_button(ViewButton.end_session())

            await menu.start()
            print(f"{interaction.id} | Start scrapping process")
            await self.scrap_and_update_menu_with_jobs(seniority, menu)
            print(f"{interaction.id} | Done")
        else:
            menu.add_page(discord.Embed(title="Vacuum Vagas",
                                        description="Bem vindo ao bot de vagas da Vacuum!\nSelecione o nível de senioridade da vaga que você deseja procurar."))
            empty_followup = ViewButton.Followup(details=ViewButton.Followup.set_caller_details(lambda: ...))
            for level in typing.get_args(SENIORITY_LEVELS):
                button = ViewButton(label=str(level), custom_id=ViewButton.ID_CALLER, followup=empty_followup)
                menu.add_button(button)

            async def update_page(payload):
                menu.remove_relay()
                selected_seniority = payload.button.label
                new_page = discord.Embed(title="Vacuum Vagas",
                                         description=f"Segura um tico ai campeão, estou buscando as vagas de {selected_seniority} ...")
                await menu.update(new_pages=[new_page], new_buttons=[ViewButton.end_session()])
                print(f"{interaction.id} | Start scrapping process")
                await self.scrap_and_update_menu_with_jobs(selected_seniority, menu)
                print(f"{interaction.id} | Done")

            menu.set_relay(update_page)
            await menu.start()

    """ Vou deixar esse código comentado para implementações futuras"""
    # @discord.app_commands.command(name='vagas')
    # async def vagas(self, interaction: Interaction):
    #     seniorities = ['Júnior', 'Pleno', 'Sênior']
    #     techs = ["Python", "ReactJs", "NodeJs", "Java", "AWS"]
    #     roles = ["Frontend", "Backend", "Tester", "Devops"]
    #     empty_followup = ViewButton.Followup(details=ViewButton.Followup.set_caller_details(lambda: ...))
    #
    #     menu = ViewMenu(interaction, menu_type=ViewMenu.TypeEmbed)
    #     menu.add_page(discord.Embed(title="Bem vindo ao Bot de Vagas da Vacuum!",
    #                                 description="Para começar, selecione o nível de senioridade que deseja procurar.",
    #                                 color=discord.Color.blurple()))
    #     buttons = []
    #
    #     async def update_page(payload):
    #         member = payload.member
    #         _button: ViewButton = payload.button
    #         selected_seniority = _button.label
    #         new_page = discord.Embed(title=f"[{selected_seniority}]", description="Agora, selecione uma tecnologia.")
    #         new_buttons = [ViewButton(label=tech, custom_id=ViewButton.ID_CALLER, followup=empty_followup) for tech in
    #                        techs]
    #         self.sections[member] = [selected_seniority]
    #         print(self.sections)
    #
    #         def on_timeout(_):
    #             if member in self.sections:
    #                 print(f"Removing {member.name} from sections!")
    #                 self.sections.pop(member)
    #                 print(self.sections)
    #
    #         menu._on_timeout_details = on_timeout
    #
    #         await menu.update(new_pages=[new_page], new_buttons=new_buttons)
    #
    #     for seniority in seniorities:
    #         button = ViewButton(label=seniority, custom_id=ViewButton.ID_CALLER, followup=empty_followup)
    #         buttons.append(button)
    #
    #     menu.add_buttons(buttons)
    #     menu.set_relay(update_page)
    #
    #     await menu.start()


async def setup(bot):
    await bot.add_cog(Vagas(bot))
