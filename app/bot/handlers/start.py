from aiogram import F, html, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

user_router = Router()

@user_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! 👋")
    
@user_router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer("Помощь по командам...")
    
@user_router.message(Command("test"))
async def command(message: Message) -> None:
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

@user_router.callback_query(F.data == "show_nfts")               
async def show_nft_handlers(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🔄 Загружаю NFT...")
    
@user_router.callback_query(F.data == "show_stats") 
async def show_stats_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🔄")
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! 👋")
    
@user_router.message(Command("help"))
async def help_hendler(message: Message):
    await message.answer("Помощь по командам...")
    
@user_router.message(Command("test"))

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
    
@user_router.callback_query(F.data == "show_nfts")               #Фильтр по "show_nfts
async def show_nft_handlers(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🔄 Загружаю NFT...")
    
@user_router.callback_query(F.data == "show_stats") #
async def show_stats_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🔄")
    
    