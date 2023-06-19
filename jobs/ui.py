import importlib
from typing import List, TypedDict

import discord
from discord import Interaction
from discord.ui import View

import utils
from consts import JOBS_SEARCH_KEYWORDS
from enums import JobLevel

importlib.reload(utils)

from utils.menu_buttons import MenuButtons
from utils.pagination import Pagination

Job = TypedDict('Job', {'Job': str, 'Apply': str})


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


class SearchResultView:
    def __init__(self, interaction: Interaction, job_level: str, keyword: str = ''):
        self.job_level = job_level
        self.keyword = keyword
        self.interaction = interaction

    async def update(self, **kwargs):
        if self.interaction.response.is_done():
            await self.interaction.edit_original_response(**kwargs)
            return
        await self.interaction.response.send_message(**kwargs)

    async def waiting_view(self):
        embed = discord.Embed(title="Vacuum Vagas",
                              description=f"Segura um tico ai campeão, estou buscando as vagas de "
                                          f"{self.keyword + ' ' if self.keyword else ''}{self.job_level} ...")
        await self.update(embed=embed, view=View())

    async def result_view(self, jobs: List[Job]):
        pages_title = f"Mostrando vagas de {self.keyword + ' ' if self.keyword else ''}{self.job_level}"
        pages_builder = JobsPageBuilder(pages_title)
        for job in jobs:
            pages_builder.add_line(f"[{job['Job']}]({job['Apply']})")
        pages = pages_builder.get_pages()

        pagination = Pagination(self.interaction, pages)
        await pagination.start()


class SearchBuilderView:
    def __init__(self, interaction: Interaction, callback, all_can_click=False):
        self.interaction = interaction
        self.callback = callback
        self.all_can_click = all_can_click
        self._keywords = list(JOBS_SEARCH_KEYWORDS.keys())
        self._job_levels = [level for level in JobLevel]
        self._embed: discord.Embed | None = None
        self._view: MenuButtons | None = None
        self._owner = self.interaction.user
        self.level: JobLevel | None = None
        self.keyword = None

    async def _job_level_selection_handler(self, index, interaction):
        if not self.all_can_click and interaction.user != self._owner:
            return
        self.level = self._job_levels[index]
        await self.go_to_keyword_view()

    async def start(self):
        self._embed = discord.Embed(title="Vacuum Vagas",
                                    description="Bem vindo ao bot de vagas da Vacuum!\nSelecione o nível de senioridade que deseja procurar.")
        buttons = [{'label': job.name} for job in self._job_levels]
        self._view = MenuButtons(owner=self.interaction.user, buttons=buttons)
        self._view.callback = self._job_level_selection_handler

        await self.interaction.response.send_message(embed=self._embed, view=self._view)

    async def _keyword_selection_handler(self, index, interaction):
        if index == 0:
            await self.goto_search()
        self.keyword = self._keywords[index - 1]
        await self.goto_search()

    async def _update_view(self):
        await self.interaction.edit_original_response(embed=self._embed, view=self._view)

    async def go_to_keyword_view(self):
        self._embed = discord.Embed(title="Vacuum Vagas",
                                    description=f"[{self.level.name}] Caso queira, uma palavra-chave pode ser adicionada na pesquisa.")
        buttons = [{'label': 'Não adicionar'}, *[{'label': keyword} for keyword in self._keywords]]

        self._view = MenuButtons(owner=self.interaction.user, buttons=buttons, max_page_buttons=15)
        self._view.callback = self._keyword_selection_handler
        self._view.update_callback = self._update_view

        await self.interaction.edit_original_response(embed=self._embed, view=self._view)

    async def goto_search(self):
        await self.callback(self.level, self.keyword)
