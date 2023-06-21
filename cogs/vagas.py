import importlib
import logging
from typing import Optional

import discord
from discord import Interaction
from discord.app_commands import Choice
from discord.ext import commands

import jobs.scraper
import jobs.ui
from enums import JobLevel

importlib.reload(jobs.scraper)
importlib.reload(jobs.ui)

from jobs.scraper import Scraper
from jobs.ui import SearchBuilderView, SearchResultView, help_view

_log = logging.getLogger('discord')


class Vagas(commands.Cog):
    """Comandos relacionados as vagas"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.scraper = Scraper()

    @commands.Cog.listener()
    async def on_ready(self):
        self.scraper.start()

    def get_helper(self):
        return ["Vagas", help_view()['embed']]

    async def do_job(self, interaction, job_level: JobLevel, keyword):
        view = SearchResultView(interaction, job_level.name, keyword)
        await view.waiting_view()

        jobs, errors = await self.scraper.scrap(job_level, keyword)
        for err in errors:
            _log.error(f"Error on scraping process. Exception : {err}", exc_info=err)
        if not jobs:
            raise RuntimeError("Cannot retrieve any jobs from scraping process.")

        await view.result_view(jobs)

    @discord.app_commands.command(name='vagas')
    @discord.app_commands.rename(job_level='senioridade', search='pesquisa')
    @discord.app_commands.describe(job_level="Escolha a senioridade da vaga.",
                                   search="Defina um parâmetro de pesquisa. Ex: python, front-end, QA.")
    @discord.app_commands.choices(job_level=[
        Choice(name='Júnior', value=JobLevel.Junior.value),
        Choice(name='Pleno', value=JobLevel.Pleno.value),
        Choice(name='Sênior', value=JobLevel.Senior.value),
    ])
    async def vagas(self, interaction: Interaction, job_level: Optional[JobLevel] = None,
                    search: Optional[str] = None):
        """Pesquise por vagas utilizando nosso bot."""

        if job_level:
            await self.do_job(interaction, job_level, search)
        else:
            async def assistant_callback(_job_level, _search):
                await self.do_job(interaction, _job_level, _search)

            assistant = SearchBuilderView(interaction, assistant_callback)
            await assistant.start()

    @vagas.error
    async def vagas_error(self, interaction: Interaction, error):
        _log.critical(f"Unexpected Internal Error: {error}", exc_info=error)
        await interaction.edit_original_response(
            content="Aconteceu algum erro enquanto tentava encontrar suas vagas. Por favor, relate o problema para algum moderador da Vacuum.",
            embed=None, view=None)


async def setup(bot):
    await bot.add_cog(Vagas(bot))
