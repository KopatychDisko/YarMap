'''Скачиваем aiogram'''

import logging
import asyncio
import os

import threading
import uvicorn

from fastapi import FastAPI

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from dotenv import load_dotenv

from handler_districts import router_districts
from handler_marker import router_marker

from command import set_command

from self_ping import scheduler


app = FastAPI()


@app.get("/")
def read_root():
    '''Заглушка'''
    return {"status": "работает"}


def run_web_server():
    '''Типо web service'''
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)


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
    
    asyncio.create_task(scheduler())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        web_thread = threading.Thread(target=run_web_server, daemon=True)
        web_thread.start()

        logging.basicConfig(
            level=logging.INFO
        )
        
        asyncio.run(main())

    except KeyboardInterrupt:
        print("Завершение работы...")
