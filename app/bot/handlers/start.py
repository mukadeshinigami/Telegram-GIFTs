from aiogram import Router, F, html
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

user_router = Router()


@user_router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}! 👋\n"
        "Напиши /help чтобы узнать команды."
    )


@user_router.message(Command("help"))
async def help_handler(message: Message):
    # Показать список команд
    text = (
        "/help — показать эту помощь\n"
        "/test — показать пример меню\n"
        "/gift_all — показать все сохранённые гифты (через API)\n"
        "/parse <id> <type> — спарсить один гифт (пример: /parse 123 lootbag)\n"
    )
    await message.answer(text)


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

