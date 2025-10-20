from aiogram.filters import Command
import aiohttp
from typing import List
from aiogram import Router
from aiogram.types import Message
from app.bot.config import Config

user_router = Router()
config = Config()

async def get_gifts() -> List[dict]:
    """Получить список гифтов через API (возвращает JSON)."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{config.API_URL}/gifts/") as resp:
            resp.raise_for_status()
            return await resp.json()
        

@user_router.message(Command("gift_all"))                         #Обработчик команды /gift_all))
async def show_gift_handler(message: Message):
    await message.answer("🔄 Загружаю гифты...")
    try:
        gifts = await get_gifts()
    except Exception:
        await message.answer("Ошибка при получении гифтов.")
        return

    for g in gifts:
        await message.answer(g if isinstance(g, str) else str(g))
