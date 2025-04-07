'''pass'''

from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message


class ChatTypeFilter(BaseFilter):
    '''For Filter type'''
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, msg: Message) -> bool:
        if isinstance(self.chat_type, str):
            return msg.chat.type == self.chat_type
        else:
            return msg.chat.type in self.chat_type
