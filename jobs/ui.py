import importlib
from typing import List, TypedDict

from discord import Interaction, Embed, Colour
from discord.ui import View

import shared.buttons_menu
import shared.pagination
from enums import JobLevel
from jobs import keywords

importlib.reload(shared.buttons_menu)
importlib.reload(shared.pagination)

from shared.buttons_menu import ButtonsMenu
from shared.pagination import Pagination

Job = TypedDict('Job', {'Job': str, 'Apply': str})

EMOJI_STR = ':memo:'
TITLE = f"{EMOJI_STR} Vacuum Vagas"
COLOUR = Colour.blurple()


class JobsPageBuilder:
    def __init__(self, pages_title, max_content_size=4096, max_lines=15):
        self.title = pages_title
        self._pages = []
        self._buffer = ""
        self._max_size = max_content_size
        self._max_lines = max_lines

    def add_line(self, content):
        if len(self._buffer) + len(content) > self._max_size or (self._buffer.count('\n') + 1) >= self._max_lines:
            new_page = Embed(title=self.title, description=self._buffer, colour=COLOUR)
            self._pages.append(new_page)
            self._buffer = ""
        self._buffer = self._buffer + ('\n' if self._buffer else '') + content

    def get_pages(self):
        last_page = Embed(title=self.title, description=self._buffer, colour=COLOUR)
        pages = [*self._pages, last_page]
        self._pages = []
        return pages


class SearchResultView:
    def __init__(self, interaction: Interaction, job_level: str, keyword: str = ''):
        self.job_level = job_level
        self.keyword = keyword
        self.interaction = interaction

    def __get_search_string(self):
        return f"{self.keyword + ' ' if self.keyword else ''}{self.job_level}"

    async def update(self, **kwargs):
        if self.interaction.response.is_done():
            await self.interaction.edit_original_response(**kwargs)
            return
        await self.interaction.response.send_message(**kwargs)

    async def waiting_view(self):
        embed = Embed(title=TITLE, colour=COLOUR,
                      description=f":coffee: Procurando por suas vagas de: {self.__get_search_string()} ...")
        await self.update(embed=embed, view=View())

    async def result_view(self, jobs: List[Job]):
        pages_title = f"{TITLE} | {self.__get_search_string()}"
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
        self._keywords = keywords.get_keyword_list()
        self._job_levels = [level for level in JobLevel]
        self._embed: Embed | None = None
        self._view: ButtonsMenu | None = None
        self._owner = self.interaction.user
        self.level: JobLevel | None = None
        self.keyword = None

    async def _job_level_selection_handler(self, index, interaction):
        if not self.all_can_click and interaction.user != self._owner:
            return
        self.level = self._job_levels[index]
        await self.go_to_keyword_view()

    async def start(self):
        self._embed = Embed(title=TITLE, colour=COLOUR,
                            description="Bem vindo ao bot de vagas da Vacuum!\nSelecione o nível de senioridade que deseja procurar.")
        buttons = [{'label': job.name} for job in self._job_levels]
        self._view = ButtonsMenu(owner=self.interaction.user, buttons=buttons)
        self._view.callback = self._job_level_selection_handler

        await self.interaction.response.send_message(embed=self._embed, view=self._view)

    async def _keyword_selection_handler(self, index, interaction):
        if index == 0:
            return await self.goto_search()
        self.keyword = self._keywords[index - 1]
        await self.goto_search()

    async def _update_view(self):
        await self.interaction.edit_original_response(embed=self._embed, view=self._view)

    async def go_to_keyword_view(self):
        self._embed = Embed(title=TITLE, colour=COLOUR,
                            description=f"[{self.level.name}] Caso queira, uma palavra-chave pode ser adicionada na pesquisa.")
        buttons = [{'label': 'Não adicionar'}, *[{'label': keyword} for keyword in self._keywords]]

        self._view = ButtonsMenu(owner=self.interaction.user, buttons=buttons, max_page_buttons=15)
        self._view.callback = self._keyword_selection_handler
        self._view.update_callback = self._update_view

        await self.interaction.edit_original_response(embed=self._embed, view=self._view)

    async def goto_search(self):
        await self.callback(self.level, self.keyword)


def help_view():
    description = f"Bem vindo ao nosso buscador de vagas.\n\n " \
                  f"Aqui na Vaccum você pode buscar por vagas de emprego enquanto interage dentro da comunidade. " \
                  f"Nosso bot trará para você todas as vagas que ele conseguir encontrar baseado nos critérios de busca " \
                  f"que você definir.\n" \
                  f"É possivel utilizar o comando /vagas passando os parametros de busca diretamente ou utilizando o " \
                  f"menu. Para iniciar o menu basta utilizar o comando sem nenhum parametro.\n\n" \
                  f"Parâmetros de busca:\n"
    embed = Embed(title=TITLE, description=description, colour=COLOUR)
    embed.add_field(name=":older_man: senioridade",
                    value="Permite selecionar o nível técnico das vagas entre Júnior, Pleno e Sênior.", inline=False)
    embed.add_field(name=":mag: pesquisa(optativo)",
                    value=" Permite adicionar uma palavra-chave ao buscador. Ex: python, front-end, AWS, QA, UI/UX.",
                    inline=False)
    return {'embed': embed}
