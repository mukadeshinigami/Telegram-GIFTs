import asyncio, logging
from os import getenv

from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher, html, F
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
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
from app.bot.handlers import parse
    
dp.include_router(start.user_router)

dp.include_router(gifts.user_router)

dp.include_router(parse.user_router)


async def set_bot_commands(bot: Bot):
    """Регистрация команд бота в меню Telegram."""
    commands = [
        BotCommand(command="start", description="🏠 Начать работу с ботом"),
        BotCommand(command="help", description="❓ Помощь и список команд"),
        BotCommand(command="gift_name", description="🔍 Найти гифт по названию"),
        BotCommand(command="get_all_gifts", description="📋 Получить все гифты"),
        BotCommand(command="health", description="💊 Проверить статус API"),
    ]
    await bot.set_my_commands(commands)

    
async def main() -> None:
    """Start bot."""
    # Регистрируем команды в меню Telegram
    await set_bot_commands(bot)
    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())