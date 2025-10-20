import asyncio, logging
from os import getenv

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher, html, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from .config import Config



config = Config()

# Инициализируем бота с правильным токеном
bot = Bot(
    token=config.BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

from app.bot.handlers import gifts
from app.bot.handlers import start
    
dp.include_router(start.user_router)

dp.include_router(gifts.user_router)

    
async def main() -> None:
    """Strart bot."""
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())