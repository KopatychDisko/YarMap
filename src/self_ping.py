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
    # Оборачиваем корутину в задачу через lambda
    aioschedule.every(1).minutes.do(lambda: asyncio.create_task(ping_self()))
    
    # Основной цикл планировщика
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)  # Задержка между проверками заданий