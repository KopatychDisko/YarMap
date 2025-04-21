'''Скачиваем aiogram'''

import logging
import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from dotenv import load_dotenv

from handler_districts import router_districts
from handler_marker import router_marker

from command import set_command


async def main():
    '''Main func'''

    load_dotenv()

    bot = Bot(
        token=os.getenv("BOT"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(router_districts, router_marker)
   
    await set_command(bot=bot)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO
    )
    
    asyncio.run(main())

