from typing import List

from discord import Interaction, Embed

from shared.buttons_menu import ButtonsMenu

BUTTONS = [{'emoji': "◀️"}, {'emoji': "⏪"}, {'emoji': "⏩"}, {'emoji': "▶"}]


class Pagination:
    def __init__(self, interaction: Interaction, pages: List[Embed]):
        self.page = 0
        self.pages = pages
        self.interaction = interaction
        self.buttons = ButtonsMenu(owner=interaction.user, buttons=BUTTONS)
        self.buttons.callback = self.__buttons_callback

    async def start(self):
        await self.update()

    async def update(self):
        msg = {'embed': self.create_embed(), 'view': self.buttons}
        if self.interaction.response.is_done():
            await self.interaction.edit_original_response(**msg)
            return
        await self.interaction.response.send_message(**msg)

    def create_embed(self):
        embed = self.pages[self.page]
        embed.set_footer(text=f"{self.page + 1}/{len(self.pages)}")
        return embed

    async def __buttons_callback(self, index, interaction):
        if index == 0:
            self.prev()
        elif index == 1:
            self.first()
        elif index == 2:
            self.last()
        elif index == 3:
            self.next()
        await self.update()

    def prev(self):
        if self.page <= 0:
            self.page = len(self.pages) - 1
        else:
            self.page -= 1

    def first(self):
        if self.page == 0:
            return
        self.page = 0

    def next(self):
        if self.page >= (len(self.pages) - 1):
            self.page = 0
        else:
            self.page += 1

    def last(self):
        if self.page >= (len(self.pages) - 1):
            return
        self.page = (len(self.pages) - 1)
