import importlib
import logging
from typing import Optional

import discord
from discord import Interaction
from discord.app_commands import Choice
from discord.ext import commands
from reactionmenu import ViewMenu, ViewButton

import jobs.scraper
import jobs.ui
from enums import Seniority

importlib.reload(jobs.scraper)
importlib.reload(jobs.ui)

from jobs.scraper import Scraper
from jobs.ui import SearchBuilderView

_log = logging.getLogger('discord')


class JobsPageBuilder:
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

    def get_helper(self):
        help_text = """• /vagas [Junior|Pleno|Senior] - Pesquise por vagas utilizando parametros de busca.
        """
        group_name = "Vagas"
        return [group_name, help_text]

    async def scrap_and_update_menu_with_jobs(self, seniority: Seniority, menu, search):
        # jobs, errors = await self.scraper.scrap(seniority, search) // Add later
        jobs, errors = await self.scraper.scrap(seniority)
        for err in errors:
            _log.error(f"Error on scraping process. Exception : {err}", exc_info=err)
        if not jobs:
            raise RuntimeError("Cannot retrieve any jobs from scraping process.")
        pages_title = f"Mostrando vagas de {search + ' ' if search else ''}{seniority.name}"
        pages_builder = JobsPageBuilder(pages_title)
        for job in jobs:
            pages_builder.add_line(f"[{job['Job']}]({job['Apply']})")
        pages = pages_builder.get_pages()
        await menu.update(new_pages=pages, new_buttons=[ViewButton.back(), ViewButton.next(), ViewButton.end_session()])

    @discord.app_commands.command(name='vagas')
    @discord.app_commands.rename(seniority='senioridade', search='pesquisa')
    @discord.app_commands.describe(seniority="Escolha a senioridade da vaga.",
                                   search="Defina um parâmetro de pesquisa. Ex: python, front-end, QA.")
    @discord.app_commands.choices(seniority=[
        Choice(name='Júnior', value=Seniority.Junior.value),
        Choice(name='Pleno', value=Seniority.Pleno.value),
        Choice(name='Sênior', value=Seniority.Senior.value),
    ])
    async def vagas(self, interaction: Interaction, seniority: Optional[Seniority] = None,
                    search: Optional[str] = None):
        """Pesquise por vagas utilizando nosso bot."""
        menu = ViewMenu(interaction, menu_type=ViewMenu.TypeEmbed, timeout=180, name=f'{interaction.id}')

        if seniority:
            menu.add_page(discord.Embed(title="Vacuum Vagas",
                                        description=f"Segura um tico ai campeão, estou buscando as vagas de {search + ' ' if search else ''}{seniority.name} ..."))
            menu.add_button(ViewButton.end_session())

            await menu.start()
            await self.scrap_and_update_menu_with_jobs(seniority, menu, search)
        else:
            async def assistant_callback(seniority, search):
                print(seniority, search)
                new_page = discord.Embed(title="Vacuum Vagas",
                                         description=f"Segura um tico ai campeão, estou buscando as vagas de {search + ' ' if search else ''}{seniority.name} ...")
                new_buttons = [ViewButton.end_session()]

                await menu.update(new_pages=[new_page], new_buttons=new_buttons)
                await self.scrap_and_update_menu_with_jobs(seniority, menu, search)

            assistant = SearchBuilderView(interaction, assistant_callback)
            await assistant.start()

    @vagas.error
    async def vagas_error(self, interaction: Interaction, error):
        await ViewMenu.stop_session(f'{interaction.id}')
        _log.critical(f"Unexpected Internal Error: {error}", exc_info=error)
        await interaction.edit_original_response(
            content="Aconteceu algum erro enquanto tentava encontrar suas vagas. Por favor, relate o problema para algum moderador da Vacuum.",
            embed=None, view=None)


async def setup(bot):
    await bot.add_cog(Vagas(bot))
