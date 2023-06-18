from typing import TypeAlias, List

from discord import Interaction, Embed

from utils.menu_buttons import MenuButtons

PageType: TypeAlias = tuple[str, Embed | List[Embed]]


class ViewMenu:
    def __init__(self, interaction: Interaction, pages: List[PageType], all_can_click=False):
        self.interaction = interaction
        self.pages = pages
        self._page = 0
        self._actual_page: PageType = self.pages[0]
        self._view = MenuButtons(buttons=[{'label': page[0]} for page in self.pages])
        self._view.callback = self.__view_callback
        self._view.update_callback = self.update
        self.all_can_click = all_can_click
        self._owner = self.interaction.user

    async def __view_callback(self, index, interaction):
        if not self.all_can_click and interaction.user != self._owner:
            return
        self._page = index
        self._actual_page = self.pages[index]
        await self.update()

    async def start(self):
        message_args = {'embeds' if isinstance(self._actual_page[1], list) else 'embed': self._actual_page[1],
                        'view': self._view}
        await self.interaction.response.send_message(**message_args)

    async def update(self):
        message_args = {'embeds' if isinstance(self._actual_page[1], list) else 'embed': self._actual_page[1],
                        'view': self._view}
        await self.interaction.edit_original_response(**message_args)
