from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
from typing import Optional
import logging
import aiohttp
import re
from urllib.parse import quote
from urllib.parse import quote
import tempfile
import os

from app.bot.config import Config
config = Config()

logger = logging.getLogger(__name__)

user_router = Router()


@user_router.message(Command("get_all_gifts"))
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
    waiting_for_names = State()

@user_router.message(Command("gift_name"))
async def gift_name_handler(message: Message, state: FSMContext):
    """
Handle the /Gift_Name command to initiate gift search by name.
This handler responds to the /Gift_Name command and prompts the user to enter
a complete gift name with number for searching. It sets the FSM state to
waiting_for_name to prepare for the next step in the gift search flow.
Args:
    message (Message): The incoming message containing the /Gift_Name command
    state (FSMContext): The finite state machine context for managing conversation state
Returns:
    None: This function doesn't return a value, it sends a response message
    and updates the FSM state
"""
    await message.answer(
        "🔍 <b>Поиск гифта по названию</b>\n\n"
        "Введите <b>полное название</b> гифта с номером:\n"
        "Например: <code>Plush Pepe #2790</code>\n\n",

        parse_mode="HTML"
    )
    
    await state.set_state(GiftForm.waiting_for_name)

@user_router.message(GiftForm.waiting_for_name)
async def process_gift_name(message: Message, state: FSMContext):
    """
Handles the gift name input in the gift search form.
This function processes the user's input when they provide a gift name to search for.
It performs the following operations:
1. Extracts and cleans the gift name from the message
2. URL-encodes the gift name for safe API requests
3. Makes an HTTP GET request to the API to find the gift by exact name
4. Handles various error cases (404 not found, connection errors, etc.)
5. Formats and displays the gift information if found
6. Clears the FSM state after processing
Args:
    message (Message): The Telegram message containing the gift name
    state (FSMContext): The finite state machine context for managing conversation state
Returns:
    None
Raises:
    aiohttp.ClientError: When there are HTTP connection issues with the API
    Exception: For any other unexpected errors during processing
Note:
    - Gift names are URL-encoded to handle special characters like '#'
    - The function generates a t.me/nft link using normalized gift name and ID
    - State is always cleared at the end, regardless of success or failure
"""
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

@user_router.message(Command("put_gift"))
async def put_gift_handler(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Введите данные для обновления гифта в формате:\n"
        "<code>Название, Новое_название, Модель, Задний_фон, Символ, Цена, Редкость, Оценочная_цена</code>\n\n"
        "Где:\n"
        "• Название - текущее имя гифта в базе\n"
        "• Новое_название - новое имя (если меняем)\n"
        "• Модель - модель гифта\n"
        "• Задний_фон - фон гифта\n"
        "• Символ - символ гифта\n"
        "• Цена - цена или 'Minted'\n"
        "• Редкость - число (или пропустить)\n"
        "• Оценочная_цена - число (или пропустить)\n\n"
        "Пример:\n"
        "<code>Plush Pepe #2790, Plush Pepe #2790, Midas Pepe, Blue, Carrot, Minted, 85, 1000</code>",
        parse_mode="HTML"
    )
    await state.set_state(GiftForm.waiting_for_names)

@user_router.message(GiftForm.waiting_for_names)
async def process_put_gift(message: Message, state: FSMContext) -> None:
    data = message.text.strip().split(",")
    if len(data) < 6 or len(data) > 8:  # минимум 6 полей, максимум 8
        await message.answer(
            "❌ Ошибка: Неверное количество параметров.\n\n"
            "Формат:\n"
            "<code>Название, Новое_название, Модель, Задний_фон, Символ, Цена, [Редкость], [Оценочная_цена]</code>\n"
            "Поля в [] - опциональные.",
            parse_mode="HTML"
        )
        return

    # Обрабатываем все поля
    current_name = data[0].strip()
    values = [item.strip() for item in data[1:]]
    
    # Проверяем числовые значения
    try:
        sale_price = values[4]
        if sale_price.lower() != 'minted':
            sale_price = int(sale_price)
    except ValueError:
        await message.answer("❌ Ошибка: Цена должна быть числом или 'Minted'")
        return

    # Опциональные поля
    rarity_score = None
    estimated_price = None
    if len(values) > 5:
        try:
            rarity_score = int(values[5]) if values[5].strip() else None
        except ValueError:
            await message.answer("❌ Ошибка: Редкость должна быть числом")
            return
    if len(values) > 6:
        try:
            estimated_price = int(values[6]) if values[6].strip() else None
        except ValueError:
            await message.answer("❌ Ошибка: Оценочная цена должна быть числом")
            return

    # Формируем payload для PUT запроса
    payload = {
        "name": values[0],
        "model": values[1],
        "backdrop": values[2],
        "symbol": values[3],
        "sale_price": sale_price,
        "rarity_score": rarity_score,
        "estimated_price": estimated_price,
        "id": 0  # ID будет игнорироваться, так как ищем по имени
    }

    config = Config()
    api_url = config.API_URL.rstrip("/")
    
    try:
        # URL encode имя гифта для безопасной передачи
        encoded_name = quote(current_name)
        async with aiohttp.ClientSession() as sess:
            async with sess.put(f"{api_url}/gifts/{encoded_name}", json=payload) as resp:
                if resp.status == 404:
                    await message.answer(f"❌ Гифт с именем '{current_name}' не найден")
                    await state.clear()
                    return
                resp.raise_for_status()
                updated_gift = await resp.json()
    except aiohttp.ClientResponseError as e:
        logger.exception("Ошибка при обновлении гифта через API: %s", e)
        await message.answer(f"❌ Ошибка API: {e.status} {e.message}")
        await state.clear()
        return
    except Exception as e:
        logger.exception("Ошибка при обновлении гифта: %s", e)
        await message.answer("❌ Не удалось обновить гифт. Проверьте подключение к API.")
        await state.clear()
        return

    # Форматируем ответ
    gift_id = updated_gift.get('id')
    name = updated_gift.get('name', '')
    
    # Формируем ссылку t.me/nft/plushpepe-2790
    normalized = normalize_name(name)
    nft_link = f"https://t.me/nft/{normalized}-{gift_id}" if normalized and gift_id else ""
    
    response = (
        f"✅ Гифт успешно обновлён!\n\n"
        f"📝 <b>Новые данные:</b>\n"
        f"• Название: {updated_gift.get('name')}\n"
        f"• Модель: {updated_gift.get('model')}\n"
        f"• Фон: {updated_gift.get('backdrop')}\n"
        f"• Символ: {updated_gift.get('symbol')}\n"
        f"• Цена: {updated_gift.get('sale_price')}\n\n"
        f"🔗 {nft_link}" if nft_link else ""
    )
    
    await message.answer(response, parse_mode="HTML")
    await state.clear()
    
    
@user_router.message(Command("download"))
async def download_handler(message: Message):
    """
    Скачивает файл базы данных с сервера и отправляет пользователю.
    """
    await message.answer("📥 Загружаю базу данных...")
    
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"{config.API_URL}/db/download") as resp:
                resp.raise_for_status()
                
                # Читаем содержимое файла
                db_content = await resp.read()
                
                # Получаем имя файла из заголовков или используем дефолтное
                content_disposition = resp.headers.get('Content-Disposition', '')
                if 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"')
                else:
                    filename = "gifts.db"
                
                # Отправляем файл пользователю напрямую из памяти
                db_file = BufferedInputFile(db_content, filename=filename)
                await message.answer_document(
                    db_file,
                    caption=f"✅ База данных ({len(db_content) // 1024} KB)"
                )
                
    except aiohttp.ClientResponseError as e:
        logger.exception("Ошибка при скачивании БД: %s", e)
        await message.answer(f"❌ Ошибка при скачивании: HTTP {e.status}")
    except Exception as e:
        logger.exception("Неожиданная ошибка при скачивании БД: %s", e)
        await message.answer("❌ Не удалось скачать базу данных. Проверьте, что API сервер запущен.")