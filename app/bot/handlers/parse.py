from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import asyncio
from typing import Optional

from app.parser.fragment import parse_fragment

user_router = Router()


@user_router.message(Command("parse"))
async def parse_command(message: Message) -> None:
	"""Команда: /parse <id> <type>

	Пример: /parse 123 lootbag
	"""
	parts = message.text.split()
	if len(parts) < 3:
		await message.answer("Использование: /parse <id> <type>\nПример: /parse 123 lootbag")
		return

	try:
		gift_id = int(parts[1])
	except ValueError:
		await message.answer("ID должен быть числом.")
		return

	gift_type = parts[2]

	await message.answer(f"Парсинг Gift #{gift_id} ({gift_type})... Пожалуйста, подождите.")

	try:
		# parse_fragment — синхронная функция (requests). Запускаем в threadpool.
		result = await asyncio.to_thread(parse_fragment, gift_id, gift_type)
	except Exception as e:
		await message.answer(f"Ошибка при парсинге: {e}")
		return

	if not result:
		await message.answer("Гифт не найден или недостаточно данных для сохранения.")
		return

	# Формируем краткий ответ пользователю
	text_lines = [
		f"ID: {result.get('id')}",
		f"Name: {result.get('name')}",
		f"Model: {result.get('model')}",
		f"Backdrop: {result.get('backdrop')}",
		f"Symbol: {result.get('symbol')}",
		f"Sale price: {result.get('sale_price')}",
	]

	await message.answer("\n".join(text_lines))
