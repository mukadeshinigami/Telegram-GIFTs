from aiogram.filters import Command
import aiohttp
from typing import List
from aiogram import Router
from aiogram.types import Message
from app.bot.config import Config

user_router = Router()
admin_router = Router()

config = Config()

async def get_gifts() -> List[dict]:
    """Получить список гифтов через API (возвращает JSON)."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{config.API_URL}/gifts/") as resp:
            resp.raise_for_status()
            return await resp.json()
        

