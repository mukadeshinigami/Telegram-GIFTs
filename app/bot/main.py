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


# Создаем экземпляр конфига
config = Config()

# Инициализируем бота с правильным токеном
bot = Bot(
    token=config.BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

from app.bot.handlers import gifts


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! 👋")
    
@dp.message(Command("help"))
async def help_hendler(message: Message):
    await message.answer("Помощь по командам...")
    
@dp.message(Command("test"))
async def commad(message: Message) -> None:
    
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(
            
        text="🎭 Показать NFT",
        callback_data="show_nfts"
    ))
    
    builder.add(
        InlineKeyboardButton(
            
        text="📊 Статистика", 
        callback_data="show_stats"
    ))
    
    await message.answer(
        "Выбери действи:",
        reply_markup=builder.as_markup()
    )
    
@dp.callback_query(F.data == "show_nfts")               #Фильтр по "show_nfts
async def show_nft_handlers(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🔄 Загружаю NFT...")
    
@dp.callback_query(F.data == "show_stats") #
async def show_stats_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🔄")
    

@dp.message(Command("gift"))
async def gift_handler(message: Message):
    await gifts.show_gift_handler(message)
    
async def main() -> None:
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())