import asyncio
import aiohttp
import aioschedule

SELF_URL = "https://yarmap.onrender.com"  # Замени на свой адрес


async def ping_self():
    '''Method for self ping'''
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SELF_URL) as resp:
                print(f"[Self-Ping] Status: {resp.status}")
    except Exception as e:
        print(f"[Self-Ping] Error: {e}")


async def scheduler():
    '''Self ping every 5 min'''
    aioschedule.every(5).minutes.do(lambda: asyncio.create_task(ping_self()))
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)