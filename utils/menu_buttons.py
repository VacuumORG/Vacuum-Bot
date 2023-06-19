"""
    -


"""
import math
from typing import TypedDict, List, Callable, Optional, Awaitable

from discord import Interaction, Member
from discord.ui import View, Button

ButtonArgs = TypedDict('ButtonArgs',
                       {'label': str, 'emoji': str},
                       total=False)


def slice_list(arr, size):
    return [[x for x in arr[i * size:(i + 1) * size]] for i in range(math.ceil(len(arr) / size))]


class MenuButtons(View):
    def __init__(self, owner: Member, buttons: List[ButtonArgs], max_page_buttons=25,
                 callback: Optional[Callable[[int, Interaction], Awaitable]] = None,
                 update_callback: Optional[Callable[[], Awaitable]] = None):
        super().__init__()
        self.buttons_args = buttons
        self.max_page_buttons = min(max_page_buttons, 25) if max_page_buttons > 0 else 25
        self.callback = callback
        self.update_callback = update_callback
        self.owner = owner
        self._page = 0

        self.pages = slice_list(self.buttons_args, self.max_page_buttons - 2)
        self._paginated = len(self.pages) > 1

        self.update_view()

    async def __back_callback(self, interaction: Interaction):
        await interaction.response.defer()
        if interaction.user != self.owner:
            return
        self._page = self._page - 1 if self._page else len(self.pages) - 1
        self.update_view()
        await self.update_callback()

    async def __next_callback(self, interaction: Interaction):
        await interaction.response.defer()
        if interaction.user != self.owner:
            return
        self._page = 0 if self._page + 1 == len(self.pages) else self._page + 1
        self.update_view()
        await self.update_callback()

    def __create_bt_callback(self, bt_index):
        async def __bt_callback(interaction: Interaction):
            await interaction.response.defer()
            if interaction.user != self.owner:
                return
            if callable(self.callback):
                await self.callback(bt_index, interaction)

        return __bt_callback

    def update_view(self):
        self.clear_items()
        if self._paginated:
            back_bt = Button(emoji="◀")
            back_bt.callback = self.__back_callback
            self.add_item(back_bt)
        for i, bt_args in enumerate(self.pages[self._page]):
            bt = Button(**bt_args)
            bt.callback = self.__create_bt_callback(i + self._page * (self.max_page_buttons - 2))
            self.add_item(bt)
        if self._paginated:
            next_bt = Button(emoji="▶")
            next_bt.callback = self.__next_callback
            self.add_item(next_bt)
