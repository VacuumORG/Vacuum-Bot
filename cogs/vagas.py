import logging
from typing import Optional

import discord
from discord import Interaction, Embed, Colour
from discord.ext import commands
from reactionmenu import ViewMenu, ViewButton

from enums import Seniority
from jobs.scraper import Scraper

_log = logging.getLogger('discord')


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

    def get_helper(self):
        embed = Embed(title=":computer: Vagas",
                      description="Dentro da Vacuum você pode pesquisar por vagas diretamente pelo discord "
                                  "utilizando nosso bot. \n\n", colour=Colour.blue())
        command_desc = "Retorna vagas obtidas no Linkedin, Nerdin e Programathor utilizando os parametros de filtragem:\n" \
                       "- Júnior|Pleno|Sênior : Filtra pela senioridade escolhida." \
                       "\n\n" \
                       "O comando pode ser utilizado sem parâmetros e o bot irá auxiliar na criação da pesquisa."
        embed.add_field(name="/vagas", value=command_desc)
        return ["Vagas", embed]

    async def scrap_and_update_menu_with_jobs(self, seniority: Seniority, menu):
        jobs, errors = await self.scraper.scrap(seniority)
        for err in errors:
            _log.error(f"Error on scraping process. Exception : {err}", exc_info=err)
        if not jobs:
            raise RuntimeError("Cannot retrieve any jobs from scraping process.")
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
        menu = ViewMenu(interaction, menu_type=ViewMenu.TypeEmbed, timeout=180, name=f'{interaction.id}')

        if seniority:
            menu.add_page(discord.Embed(title="Vacuum Vagas",
                                        description=f"Segura um tico ai campeão, estou buscando as vagas de {seniority.name} ..."))
            menu.add_button(ViewButton.end_session())

            await menu.start()
            await self.scrap_and_update_menu_with_jobs(seniority, menu)
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
                await self.scrap_and_update_menu_with_jobs(Seniority[selected_seniority], menu)

            menu.set_relay(update_page)
            await menu.start()

    @vagas.error
    async def vagas_error(self, interaction: Interaction, error):
        await ViewMenu.stop_session(f'{interaction.id}')
        _log.critical(f"Unexpected Internal Error: {error}", exc_info=error)
        await interaction.edit_original_response(
            content="Aconteceu algum erro enquanto tentava encontrar suas vagas. Por favor, relate o problema para algum moderador da Vacuum.",
            embed=None, view=None)


async def setup(bot):
    await bot.add_cog(Vagas(bot))
