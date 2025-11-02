from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
from typing import Optional
import logging
import aiohttp
import re
from urllib.parse import quote

from app.bot.config import Config

logger = logging.getLogger(__name__)

user_router = Router()


@user_router.message(Command("Get_All_Gifts"))
async def parse_command(message: Message):

    """
    Handle the /Get_All_Gifts command to fetch and display all available gifts.
    This function retrieves all gifts from the API endpoint, processes each gift
    to create Telegram NFT links, and sends them to the user. The links are
    formatted as t.me/nft/{normalized_name}-{gift_id}.
    Args:
        message (Message): The incoming Telegram message containing the command.
    Returns:
        None: This function sends responses directly to the user via message.answer().
    Raises:
        Exception: Catches and logs API connection errors, gift processing errors,
                and other exceptions that may occur during execution.
    Note:
        - If the API request fails, an error message is sent to the user
        - If no gifts are available, an appropriate message is displayed
        - Gift names are normalized before creating links
        - Only gifts with valid ID and name/model are processed
        - A summary message is sent if no links could be generated
    """
    config = Config()
    api_url = config.API_URL.rstrip("/")

    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"{api_url}/gifts/") as resp:
                resp.raise_for_status()
                gifts = await resp.json()
    except Exception as e:
        logger.exception("Failed to fetch gifts from API: %s", e)
        await message.answer("Ошибка при получении списка гифтов от API.")
        return

    if not gifts:
        await message.answer("Список гифтов пуст.")
        return

    sent = 0
    for g in gifts:
        try:
            gid = g.get("id")
            name = g.get("name") or g.get("model") or ""
            normalized = normalize_name(name)
            if not normalized or not gid:
                continue
            link = f"t.me/nft/{normalized}-{gid}"
            await message.answer(link)
            sent += 1
        except Exception:
            logger.exception("Failed to process gift: %s", g)

    if sent == 0:
        await message.answer("Не удалось сформировать ни одной ссылки.")

def normalize_name(name: str) -> str:
    """Normalize a gift name for URL path.

    Examples:
      'Plush Pepe #2773' -> 'plushpepe'
      'Hanging Star' -> 'hangingstar'
    """
    if not name:
        return ""
    # Remove trailing ' #digits' pattern
    name = re.sub(r"\s*#\d+$", "", name)
    # Remove all non-alphanumeric characters
    name = re.sub(r"[^A-Za-z0-9]", "", name)
    return name.lower()


class GiftForm(StatesGroup):
    waiting_for_name = State()

@user_router.message(Command("Gift_Name"))
async def gift_name_handler(message: Message, state: FSMContext):
    
    await message.answer(
        "🔍 <b>Поиск гифта по названию</b>\n\n"
        "Введите <b>полное название</b> гифта с номером:\n"
        "Например: <code>Plush Pepe #2790</code>\n\n",

        parse_mode="HTML"
    )
    
    await state.set_state(GiftForm.waiting_for_name)

@user_router.message(GiftForm.waiting_for_name)
async def process_gift_name(message: Message, state: FSMContext):
    gift_name = message.text.strip()
    
    # Логируем что получили от пользователя
    logger.info(f"Поиск гифта по имени: '{gift_name}'")
    
    config = Config()
    api_url = config.API_URL.rstrip("/")
    
    # URL-кодируем имя гифта (особенно важно для символа #)
    encoded_gift_name = quote(gift_name, safe='')
    
    # Пытаемся получить гифт по точному имени
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"{api_url}/gifts/{encoded_gift_name}") as resp:
                if resp.status == 404:
                    await message.answer(
                        f"❌ Гифт с именем <b>'{gift_name}'</b> не найден.\n\n"
                        f"💡 <b>Подсказка:</b> Введите полное имя с номером,\n"
                        f"например: <code>Plush Pepe #2790</code>",
                        parse_mode="HTML"
                    )
                    await state.clear()
                    return
                resp.raise_for_status()
                gift = await resp.json()
    except aiohttp.ClientError as e:
        logger.exception("Ошибка HTTP при запросе гифта из API: %s", e)
        await message.answer("❌ Не удалось подключиться к API. Проверьте, что сервер запущен.")
        await state.clear()
        return
    except Exception as e:
        logger.exception("Неожиданная ошибка при запросе гифта из API: %s", e)
        await message.answer("❌ Произошла ошибка при обработке запроса.")
        await state.clear()
        return
    
    # Извлекаем данные
    gift_id = gift.get("id")
    name = gift.get("name", "")
    model = gift.get("model", "")
    backdrop = gift.get("backdrop", "")
    symbol = gift.get("symbol", "")
    sale_price = gift.get("sale_price", "")
    
    # Формируем ссылку t.me/nft/plushpepe-2790
    # normalize_name убирает "#2773" и спецсимволы, оставляя только "plushpepe"
    normalized = normalize_name(name)
    nft_link = f"https://t.me/nft/{normalized}-{gift_id}" if normalized and gift_id else "—"
    
    # Формируем красивый ответ
    response = (
        f"🎁 <b>Гифт найден!</b>\n\n"
        f"📦 <b>Название:</b> {name}\n"
        f"📝 <b>Детали:</b>\n"
        f"• Model: {model}\n"
        f"• Backdrop: {backdrop}\n"
        f"• Symbol: {symbol}\n"
        f"• Sale Price: {sale_price}\n\n"
        f"🔗{nft_link}"
    )
    
    await message.answer(response, parse_mode="HTML")
    await state.clear()