import discord
from discord import Interaction

from consts import JOBS_SEARCH_KEYWORDS
from enums import Seniority
from utils.menu_buttons import MenuButtons


class SearchBuilderView:
    def __init__(self, interaction: Interaction, callback):
        self.interaction = interaction
        self.callback = callback
        self._keywords = list(JOBS_SEARCH_KEYWORDS.keys())
        self._job_levels = [level for level in Seniority]
        self._embed: discord.Embed | None = None
        self._view: MenuButtons | None = None
        self.level: Seniority | None = None
        self.keyword = None

    async def _job_level_selection_handler(self, index, interaction):
        self.level = self._job_levels[index]
        await self.go_to_keyword_view()

    async def start(self):
        self._embed = discord.Embed(title="Vacuum Vagas",
                                    description="Bem vindo ao bot de vagas da Vacuum!\nSelecione o nível de senioridade que deseja procurar.")
        buttons = [{'label': job.name} for job in self._job_levels]
        self._view = MenuButtons(buttons)
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

        self._view = MenuButtons(buttons, max_page_buttons=15)
        self._view.callback = self._keyword_selection_handler
        self._view.update_callback = self._update_view

        await self.interaction.edit_original_response(embed=self._embed, view=self._view)

    async def goto_search(self):
        await self.callback(self.level, self.keyword)
