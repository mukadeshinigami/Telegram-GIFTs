import os
import asyncio
import time
import logging
import uuid

from typing import List, Optional

import aiohttp
import uvicorn # uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

import sqlalchemy
# Импортируем модели и функции относительно пакета `app`
from .DB.models import Gift

# Импортируем наши функции
from .DB.create_database import connect_db, create_database
from .bot.config import Config
from .parser.fragment import parse_fragment

# Ensure logging is initialized (app package init also calls this)
from app.logging_config import get_logger, new_error_id

logger = get_logger(__name__)

DB_PATH = (
    "/home/ame/Programming/python/project/Telegram-GIFTs/gifts.db"
)

config = Config()


app = FastAPI(
    title="Telegram Gifts Parser API",
    description=(
        "API для парсинга и управления гифтами с fragment.com"
    ),
    version="1.0.0",
)


class GiftBase(BaseModel):
    """Базовая модель данных гифта."""

    id: int = Field(description="Уникальный идентификатор гифта")
    name: str = Field(description="Название гифта")
    model: str = Field(description="Модель гифта")
    backdrop: str = Field(description="Фон гифта")
    symbol: str = Field(description="Символ гифта")
    # sale_price may be an integer price or a string status like 'Minted'
    sale_price: int | str | None = Field(description="Цена продажи или статус 'Minted'")


class GiftCreate(BaseModel):
    """Модель для создания запроса на парсинг гифта."""

    gift_id: int = Field(
        gt=0, description="ID гифта для парсинга (должен быть больше 0)"
    )
    user_selection_gifts: str = Field(
        description="Тип гифта (например: lootbag)"
    )


class ParseTask(BaseModel):
    """Модель для запуска фоновой задачи парсинга."""

    start_id: int = Field(gt=0, description="Начальный ID диапазона для парсинга")
    end_id: int = Field(gt=0, description="Конечный ID диапазона для парсинга")
    user_selection_gifts: str = Field(description="Тип гифта для парсинга")
    delay: float = Field(
        default=1.0,
        ge=0.1,
        le=5.0,
        description="Задержка между запросами в секундах (0.1-5.0)",
    )


# Глобальные переменные для управления задачами.
active_tasks = {}


class GiftUpgrade(BaseModel):
    """Модель для обновления информации о гифтах."""

    id: int = Field(description="ID гифта для обновления")
    name: str = Field(description="Название гифта")
    model: str = Field(description="Модель гифта")
    backdrop: str = Field(description="Фон гифта")
    symbol: str = Field(description="Символ гифта")
    # Allow numeric price or status string (e.g. 'Minted')
    sale_price: int | str | None = Field(description="Цена продажи или статус 'Minted'")
    rarity_score: Optional[int] = Field(description="Новый показатель редкости гифта")
    estimated_price: Optional[int] = Field(description="Новая оценочная цена гифта")


class GiftPatch(BaseModel):
    """Модель для частичного обновления гифта (PATCH)."""

    # Allow patching sale_price to an int or to a string status like 'Minted'
    sale_price: Optional[int | str] = Field(
        None, description="Новая цена (или 'Minted')"
    )


@app.get("/")
async def root():
    """Корневой endpoint - информация о API."""

    return {
        "message": "Telegram Gifts Parser API",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "gifts": "/gifts/",
            "parse": "/parse/",
            "batch_parse": "/parse/batch/",
        },
    }


@app.get("/health")
async def health_check():
    """Проверка статуса работы API и базы данных."""

    try:
        # 1. ✅ Проверяем соединение с БД
        with connect_db() as session:
            # 2. ✅ Пытаемся выполнить простой запрос
            gift_count = session.query(Gift).count()

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "database": "connected",
            "total_gifts": gift_count,
        }
    except Exception as e:
        err_id = new_error_id()
        logger.exception("Ошибка подключения к БД (%s)", err_id)
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера (id={err_id})")


@app.get("/gifts/", response_model=List[GiftBase])
async def get_all_gifts(
    limit: int = 100,
    offset: int = 0
):
    """
    Получить список всех гифтов из базы данных
    """
    try:
        with connect_db() as session:
            gifts = session.query(Gift).order_by(Gift.id).limit(limit).offset(offset).all()
            return [
                GiftBase(
                    id=g.id,
                    name=g.name,
                    model=g.model,
                    backdrop=g.backdrop,
                    symbol=g.symbol,
                    sale_price=g.sale_price
                    
                    
                )
                for g in gifts
            ]
    except Exception as e:
        err_id = new_error_id()
        logger.exception("Ошибка при получении данных из БД (%s)", err_id)
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера (id={err_id})")


@app.get("/gifts/{gift_name}", response_model=GiftBase)
async def get_gift_by_id(gift_name: str):
    """
    Получить информацию о конкретном гифте по имени

    - **gift_name**: Имя гифта для поиска в базе данных (например: "Plush Pepe #2790")
    """
    try:
        with connect_db() as session:
            gift = session.query(Gift).filter(Gift.name == gift_name).first()
            if not gift:
                raise HTTPException(
                    status_code=404,
                    detail=f"Гифт с именем '{gift_name}' не найден в базе данных"
                )

            return GiftBase(
                id=gift.id,
                name=gift.name,
                model=gift.model,
                backdrop=gift.backdrop,
                symbol=gift.symbol,
                sale_price=gift.sale_price
            )

    except HTTPException:
        raise
    except Exception as e:
        err_id = new_error_id()
        logger.exception("Ошибка при поиске гифта в БД (%s)", err_id)
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера (id={err_id})")


@app.post("/parse/", response_model=GiftBase)
async def parse_single_gift(gift_data: GiftCreate):
    """
    Спарсить и сохранить в БД один гифт по ID

    - **gift_id**: ID гифта для парсинга
    - **user_selection_gifts**: Тип гифта (например: lootbag)
    """
    try:
        result = parse_fragment(gift_data.gift_id, gift_data.user_selection_gifts)

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Гифт с ID {gift_data.gift_id} не найден или содержит недостаточно данных для парсинга"
            )

        return GiftBase(
            id=result["number_iteration"],
            name=result["name"],
            model=result["model"],
            backdrop=result["backdrop"],
            symbol=result["symbol"],
            sale_price=result["sale_price"]
        )

    except HTTPException:
        raise
    except Exception as e:
        err_id = new_error_id()
        logger.exception("Ошибка при парсинге гифта %s (%s)", gift_data.gift_id, err_id)
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера (id={err_id})")


@app.put("/gifts/{gift_name}", response_model=GiftBase)
async def update_gift_by_name(name: Optional[str], gift_data: GiftUpgrade):
    """
    Ручное обновление гифта по имени (name)
    - **gift_name**: имя гифта для обновления
    """
    try:
        with connect_db() as session:
            gift = session.query(Gift).filter(Gift.name == name).first()
            if not gift:
                raise HTTPException(status_code=404, detail="Gift not found")

            # Применяем новые данные (аналогично примеру выше)
            for field, value in gift_data.dict(exclude_unset=True).items():
                # Если обновляют sale_price — сохраняем как строку (поддерживаем статусы вроде 'Minted' и числа)
                if field == "sale_price":
                    setattr(gift, field, str(value) if value is not None else None)
                else:
                    setattr(gift, field, value)

            session.commit()
            session.refresh(gift)

            return GiftBase(
                id=gift.id,
                name=gift.name,
                model=gift.model,
                backdrop=gift.backdrop,
                symbol=gift.symbol,
                sale_price=gift.sale_price
            )
    except HTTPException:
        raise
    except Exception as e:
        err_id = new_error_id()
        logger.exception("Ошибка при парсинге гифта %s (%s)", gift_data.name, err_id)
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера (id={err_id})")


@app.patch("/gifts/{gift_name}", response_model=GiftBase)
async def patch_gift(name: Optional[str], patch: GiftPatch):
    """Частичное обновление гифта по его полю `id` (обновляет `name` и/или `sale_price`).

    - **gift_id**: числовой ID (поле `id` в таблице)
    - payload: объект с необязательными полями `name` и `price`
    """
    try:
        data = patch.dict(exclude_unset=True)
        if not data:
            raise HTTPException(status_code=400, detail="Нет полей для обновления")

        with connect_db() as session:
            # Ищем по числовому полю id в модели
            gift = session.query(Gift).filter(Gift.name == name).first()
            if not gift:
                raise HTTPException(status_code=404, detail=f"Гифт с именем {name} не найден")

            # Обновляем только переданные поля
            if "name" in data:
                gift.name = data["name"]
            if "sale_price" in data:
                # Сохраняем как строку — это позволяет хранить статусы ('Minted') и числа
                gift.sale_price = str(data["sale_price"]) if data["sale_price"] is not None else None

            session.commit()
            session.refresh(gift)

            # Приводим sale_price к int для ответа (если необходимо)
            sp = gift.sale_price
            try:
                sp = int(sp) if sp is not None else None
            except Exception:
                # если хранится строка нечислового формата (например 'Minted'), оставим как есть
                pass

            return GiftBase(
                id=gift.id,
                name=gift.name,
                model=gift.model,
                backdrop=gift.backdrop,
                symbol=gift.symbol,
                sale_price=sp
            )
    except HTTPException:
        raise
    except Exception as e:
        err_id = new_error_id()
        logger.exception("Ошибка при обновлении гифта (%s)", err_id)
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера (id={err_id})")


@app.get("/db/download")
def download_db():
    if not os.path.isfile(DB_PATH):
        raise HTTPException(status_code=404, detail="Database file not found")
    file_like = open(DB_PATH, mode="rb")
    return StreamingResponse(file_like, media_type="application/octet-stream", headers={
        "Content-Disposition": f"attachment; filename={os.path.basename(DB_PATH)}"
    })


##############################################################
# Фоновый парсинг диапазона гифтов
##############################################################

async def background_parsing(
    task_id: str,
    start_id: int,
    end_id: int,
    user_selection_gifts: str,
    delay: float
):
    """
    Фоновая задача для массового парсинга диапазона гифтов

    - **task_id**: Уникальный идентификатор задачи
    - **start_id**: Начальный ID диапазона
    - **end_id**: Конечный ID диапазона
    - **user_selection_gifts**: Тип гифтов
    - **delay**: Задержка между запросами
    """
    success = 0
    failed = 0

    for gift_id in range(start_id, end_id + 1):
        try:
            result = parse_fragment(gift_id, user_selection_gifts)
            if result:
                success += 1
            else:
                failed += 1

            # Обновляем прогресс задачи
            active_tasks[task_id] = {
                "current": gift_id,
                "total": end_id - start_id + 1,
                "success": success,
                "failed": failed,
                "status": "running",
                "progress": f"{((gift_id - start_id + 1) / (end_id - start_id + 1)) * 100:.1f}%"
            }

            await asyncio.sleep(delay)

        except Exception as e:
            failed += 1
            err_id = new_error_id()
            logger.exception("Ошибка при парсинге гифта %s (%s)", gift_id, err_id)

    # Завершаем задачу
    active_tasks[task_id]["status"] = "completed"
    active_tasks[task_id]["completed_at"] = time.time()


@app.post("/parse/batch/")
async def start_batch_parsing(task: ParseTask, background_tasks: BackgroundTasks):
    """
    Запустить фоновую задачу для парсинга диапазона гифтов

    - **start_id**: Начальный ID диапазона
    - **end_id**: Конечный ID диапазона
    - **user_selection_gifts**: Тип гифтов
    - **delay**: Задержка между запросами (по умолчанию 1.0 секунда)
    """
    if task.start_id > task.end_id:
        raise HTTPException(
            status_code=400,
            detail="Начальный ID не может быть больше конечного ID"
        )

    task_id = f"task_{int(time.time())}"

    active_tasks[task_id] = {
        "current": task.start_id,
        "total": task.end_id - task.start_id + 1,
        "success": 0,
        "failed": 0,
        "status": "starting",
        "progress": "0%",
        "started_at": time.time()
    }

    background_tasks.add_task(
        background_parsing,
        task_id, task.start_id, task.end_id, task.user_selection_gifts, task.delay
    )

    return {
        "task_id": task_id,
        "message": "Задача массового парсинга запущена",
        "details": {
            "range": f"{task.start_id}-{task.end_id}",
            "type": task.user_selection_gifts,
            "delay": task.delay
        }
    }


# @app.get("/tasks/{task_id}")
# async def get_task_status(task_id: str):
#     """
#     Получить статус и прогресс фоновой задачи парсинга
#
#     - **task_id**: Идентификатор задачи полученный при запуске парсинга
#     """
#     if task_id not in active_tasks:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Задача с ID {task_id} не найдена"
#         )
#
#     return active_tasks[task_id]

# @app.get("/tasks/")
# async def get_all_tasks():
#     """
#     Получить список всех активных и завершенных задач
#     """
#     return {
#         "active_tasks": {
#             task_id: info for task_id, info in active_tasks.items()
#             if info.get("status") != "completed"
#         },
#         "completed_tasks": {
#             task_id: info for task_id, info in active_tasks.items()
#             if info.get("status") == "completed"
#         },
#         "total_tasks": len(active_tasks)
#     }


async def get_gifts():
    """
    Получить список гифтов через API (возвращает JSON).
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{config.API_URL}/gifts/") as response:
            return await response.json()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )