from typing import Optional

import discord
from discord import Interaction
from discord.ext import commands
from reactionmenu import ViewMenu, ViewButton

from enums import Seniority
from jobs.scraper import Scraper


class PageBuilder:
    def __init__(self, pages_title, max_content_size=4096, max_lines=15):
        self.title = pages_title
        self._pages = []
        self._buffer = ""
        self._max_size = max_content_size
        self._max_lines = max_lines

    def add_line(self, content):
        if len(self._buffer) + len(content) > self._max_size or (self._buffer.count('\n') + 1) >= self._max_lines:
            new_page = discord.Embed(title=self.title, description=self._buffer)
            self._pages.append(new_page)
            self._buffer = ""
        self._buffer = self._buffer + ('\n' if self._buffer else '') + content

    def get_pages(self):
        last_page = discord.Embed(title=self.title, description=self._buffer)
        pages = [*self._pages, last_page]
        self._pages = []
        return pages


class Vagas(commands.Cog):
    """Comandos relacionados as vagas"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.scraper = Scraper()

    async def scrap_and_update_menu_with_jobs(self, seniority: Seniority, menu):
        jobs = await self.scraper.scrap(seniority)
        pages_title = f"Mostrando vagas de {seniority.name}"
        pages_builder = PageBuilder(pages_title)
        for job in jobs:
            pages_builder.add_line(f"[{job['Job']}]({job['Apply']})")
        pages = pages_builder.get_pages()
        await menu.update(new_pages=pages, new_buttons=[ViewButton.back(), ViewButton.next(), ViewButton.end_session()])

    @discord.app_commands.command(name='vagas')
    @discord.app_commands.rename(seniority='senioridade')
    @discord.app_commands.describe(seniority="Escolha a senioridade da vaga.")
    async def vagas(self, interaction: Interaction, seniority: Optional[Seniority] = None):
        """Pesquise por vagas utilizando nosso bot."""
        menu = ViewMenu(interaction, menu_type=ViewMenu.TypeEmbed, timeout=180)

        if seniority:
            menu.add_page(discord.Embed(title="Vacuum Vagas",
                                        description=f"Segura um tico ai campeão, estou buscando as vagas de {seniority.name} ..."))
            menu.add_button(ViewButton.end_session())

            await menu.start()
            print(f"{interaction.id} | Start scrapping process")
            await self.scrap_and_update_menu_with_jobs(seniority, menu)
            print(f"{interaction.id} | Done")
        else:
            menu.add_page(discord.Embed(title="Vacuum Vagas",
                                        description="Bem vindo ao bot de vagas da Vacuum!\nSelecione o nível de senioridade da vaga que você deseja procurar."))
            empty_followup = ViewButton.Followup(details=ViewButton.Followup.set_caller_details(lambda: ...))
            for level in Seniority:
                button = ViewButton(label=str(level.name), custom_id=ViewButton.ID_CALLER, followup=empty_followup)
                menu.add_button(button)

            async def update_page(payload):
                menu.remove_relay()
                selected_seniority = payload.button.label
                new_page = discord.Embed(title="Vacuum Vagas",
                                         description=f"Segura um tico ai campeão, estou buscando as vagas de {selected_seniority} ...")
                await menu.update(new_pages=[new_page], new_buttons=[ViewButton.end_session()])
                print(f"{interaction.id} | Start scrapping process")
                await self.scrap_and_update_menu_with_jobs(Seniority[selected_seniority], menu)
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
