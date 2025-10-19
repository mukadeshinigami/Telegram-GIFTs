from aiogram.filters import Command

from app.bot.main import dp
from aiogram.types import Message

@dp.message(Command("gift"))
async def show_gift_handler(message: Message):
    # импорт внутри функции, чтобы избежать циклического импорта
    from app.main import get_gifts

    await message.answer("🔄 Загружаю гифты...")
    gifts = await get_gifts()  # пример использования
    # ... обработка и отправка gifts ...
