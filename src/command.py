'''Set commands'''

from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats
from aiogram import Bot


async def set_command(bot: Bot):
    'Set bot commands'
    commands = [
        BotCommand(command='start', description='Приветствие'),
        BotCommand(command='cancel', description='Вернуться к началу'),
        BotCommand(command='change', description='Меняем или что то добавляем на карту'),
        BotCommand(command='give_map', description='Высылаю Вам карту')
    ]

    await bot.set_my_commands(commands, BotCommandScopeAllPrivateChats())
