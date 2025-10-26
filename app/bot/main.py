import asyncio, logging
from os import getenv

from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher, html, F
from aiogram.enums import ParseMode
from .config import Config
import sys


config = Config()

# Проверим наличие токена и выведем понятное сообщение, если он не задан
token = config.BOT_TOKEN
if not token:
    # печатаем в stderr короткое дружелюбное сообщение и выходим
    sys.stderr.write(
        "Error: BOT_TOKEN is not set.\n"
        "Set it in a .env file or as an environment variable (BOT_TOKEN=...) or create app/bot/config.py.\n"
    )
    sys.exit(1)

# Инициализируем бота с правильным токеном
bot = Bot(
    token=token,
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