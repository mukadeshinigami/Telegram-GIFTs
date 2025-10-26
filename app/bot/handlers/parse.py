from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import asyncio
from typing import Optional
import logging
import aiohttp
import re

from app.bot.config import Config

logger = logging.getLogger(__name__)

user_router = Router()


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

