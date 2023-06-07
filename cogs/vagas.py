import logging
from typing import Optional

import discord
from discord import Interaction
from discord.app_commands import Choice
from discord.ext import commands
from reactionmenu import ViewMenu, ViewButton

from consts import JOBS_SEARCH_KEYWORDS
from enums import Seniority
from jobs.scraper import Scraper

_log = logging.getLogger('discord')

BACK_BUTTON_LABEL = "◀️"
NEXT_BUTTON_LABEL = "▶️"
CANCEL_BUTTON_LABEL = "❌"


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


class JobsSearchAssistant:
    def __init__(self, menu: ViewMenu, callback):
        self.menu = menu
        self.callback = callback
        self._empty_follow_up = ViewButton.Followup(details=ViewButton.Followup.set_caller_details(lambda: ...))
        self.buttons_page = 0
        self.seniority: Seniority | None = None
        self.keyword = None
        self.setup_job_level_selection()

    def _create_button(self, **kwargs):
        return ViewButton(**kwargs, custom_id=ViewButton.ID_CALLER,
                          followup=self._empty_follow_up)

    def setup_job_level_selection(self):
        self.menu.add_page(discord.Embed(title="Vacuum Vagas",
                                         description="Bem vindo ao bot de vagas da Vacuum!\nSelecione o nível de senioridade que deseja procurar."))
        empty_followup = ViewButton.Followup(details=ViewButton.Followup.set_caller_details(lambda: ...))

        buttons = [ViewButton(label=str(level.name), custom_id=ViewButton.ID_CALLER, followup=empty_followup) for level
                   in Seniority]
        self.menu.add_buttons(buttons)

        async def job_level_handler(payload):
            self.menu.remove_relay()
            selected_seniority = payload.button.label
            self.seniority = Seniority[selected_seniority]
            await self.setup_keyword_selection()

        self.menu.set_relay(job_level_handler)

    async def setup_keyword_selection(self):
        new_page = discord.Embed(title="Vacuum Vagas",
                                 description=f"[{self.seniority.name}] Caso queira, adicione uma palavra-chave na pesquisa.")

        if len(JOBS_SEARCH_KEYWORDS) <= 25:
            new_buttons = [
                ViewButton(label=str(keyword), custom_id=ViewButton.ID_CALLER, followup=self._empty_follow_up) for
                keyword in JOBS_SEARCH_KEYWORDS.keys()]
        else:
            new_buttons = []
            if self.buttons_page > 0:
                new_buttons.append(self._create_button(emoji=BACK_BUTTON_LABEL))
            new_buttons.append(self._create_button(emoji=CANCEL_BUTTON_LABEL))
            lower_index = self.buttons_page * 22
            higher_index = (self.buttons_page + 1) * 22
            new_buttons.extend([self._create_button(label=str(keyword)) for
                                keyword in list(JOBS_SEARCH_KEYWORDS.keys())[lower_index:higher_index]])
            if higher_index < len(JOBS_SEARCH_KEYWORDS):
                new_buttons.append(self._create_button(emoji=NEXT_BUTTON_LABEL))

        async def keyword_selection_handler(payload):
            if payload.button.emoji:
                if payload.button.emoji.name == BACK_BUTTON_LABEL:
                    self.buttons_page -= 1
                    return await self.setup_keyword_selection()
                if payload.button.emoji.name == NEXT_BUTTON_LABEL:
                    self.buttons_page += 1
                    return await self.setup_keyword_selection()
                if payload.button.emoji.name == CANCEL_BUTTON_LABEL:
                    return await self.goto_search()
            else:
                self.keyword = payload.button.label
                await self.goto_search()

        self.menu.set_relay(keyword_selection_handler)
        await self.menu.update(new_pages=[new_page], new_buttons=new_buttons)

    async def goto_search(self):
        await self.callback(self.seniority, self.keyword)

    async def start(self):
        await self.menu.start()


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

            assistant = JobsSearchAssistant(menu, assistant_callback)
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
