from aiogram import Router, F, html
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
import json
import html as _html
import logging
import aiohttp

from app.bot.config import Config

logger = logging.getLogger(__name__)
config = Config()

user_router = Router()


@user_router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}! 👋\n"
        "Напиши /help чтобы узнать команды."
    )


@user_router.message(Command("help"))
async def help_handler(message: Message):
    text = (
        "📋 <b>Доступные команды:</b>\n\n"
        
        "🎁 <b>Работа с гифтами:</b>\n"
        "/gift_name — найти гифт по полному названию\n"
        "/get_all_gifts — получить список всех гифтов\n\n"
        
        "⚙️ <b>Система:</b>\n"
        "/health — проверить статус API сервера\n"
        "/root — информация об API\n\n"
        
        "ℹ️ <b>Общее:</b>\n"
        "/start — начать работу с ботом\n"
        "/help — показать это сообщение\n"
        "/test — показать пример меню\n\n"
        
        "💡 <b>Подсказка:</b>\n"
        "При поиске гифта указывайте полное название с номером,\n"
        "например: <code>Plush Pepe #2790</code>"
    )
    await message.answer(text, parse_mode="HTML")
  

@user_router.message(Command("test"))
    # Показать пример меню
async def test_handler(message: Message) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🎭 Показать NFT", callback_data="show_nfts"))
    builder.add(InlineKeyboardButton(text="📊 Статистика", callback_data="show_stats"))
    await message.answer("Выбери действие:", reply_markup=builder.as_markup())


@user_router.callback_query(F.data == "show_nfts")
async def show_nfts_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🔄 Загружаю NFT...")


@user_router.callback_query(F.data == "show_stats")
async def show_stats_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🔄")


@user_router.message(Command("root"))
async def root_command(message: Message) -> None:
  """Возвращает реальную информацию из корневого эндпоинта API (app.main.root)."""
  try:
    async with aiohttp.ClientSession() as session:
      async with session.get(f"{config.API_URL}/") as response:
        if response.status != 200:
          await message.answer(f"❌ Ошибка API: статус {response.status}")
          return
        data = await response.json() 
  except Exception as e:
    logger.exception("Ошибка при вызове API root: %s", e)
    await message.answer("❌ Не удалось подключиться к API")
    return

  pretty = json.dumps(data, ensure_ascii=False, indent=2)
  # Escape for HTML pre block
  escaped = _html.escape(pretty)
  await message.answer(f"<pre>{escaped}</pre>", parse_mode="HTML")


@user_router.message(Command("health"))
async def health_command(message: Message) -> None:
  """Возвращает состояние здоровья из эндпоинта API (app.main.health)."""
  try:
    async with aiohttp.ClientSession() as session:
      async with session.get(f"{config.API_URL}/health") as response:
        if response.status != 200:
          await message.answer(f"❌ Ошибка API: статус {response.status}")
          return
        data = await response.json()
  except Exception as e:
    logger.exception("Ошибка при вызове API health: %s", e)
    await message.answer("❌ Не удалось подключиться к API")
    return

  pretty = json.dumps(data, ensure_ascii=False, indent=2)
  # Escape for HTML pre block
  escaped = _html.escape(pretty)
  await message.answer(f"<pre>{escaped}</pre>", parse_mode="HTML")