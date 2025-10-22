from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
import asyncio, uvicorn, aiohttp
import time
import sqlalchemy
from DB.models import Gift

# Импортируем наши функции
from parser.fragment import parse_fragment
from DB.create_database import create_database, connect_db
from bot.config import Config


config = Config()

app = FastAPI(
    title="Telegram Gifts Parser API",
    description="API для парсинга и управления гифтами с fragment.com",
    version="1.0.0"
)


# Модели Pydantic для валидации данных
class GiftBase(BaseModel):
    """Базовая модель данных гифта"""
    id: int = Field(description="Уникальный идентификатор гифта")
    name: str = Field(description="Название гифта")
    model: str = Field(description="Модель гифта")
    backdrop: str = Field(description="Фон гифта")
    symbol: str = Field(description="Символ гифта")
    sale_price: str = Field(description="Цена продажи или статус 'Minted'")

class GiftCreate(BaseModel):
    """Модель для создания запроса на парсинг гифта"""
    gift_id: int = Field(gt=0, description="ID гифта для парсинга (должен быть больше 0)")
    user_selection_gifts: str = Field(description="Тип гифта (например: lootbag)")


class ParseTask(BaseModel):
    """Модель для запуска фоновой задачи парсинга"""
    start_id: int = Field(gt=0, description="Начальный ID диапазона для парсинга")
    end_id: int = Field(gt=0, description="Конечный ID диапазона для парсинга")
    user_selection_gifts: str = Field(description="Тип гифта для парсинга")
    delay: float = Field(default=1.0, ge=0.1, le=5.0, description="Задержка между запросами в секундах (0.1-5.0)")

# Глобальные переменные для управления задачами
active_tasks = {}


@app.get("/")
async def root():
    """Корневой endpoint - информация о API"""
    return {
        "message": "Telegram Gifts Parser API", 
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "gifts": "/gifts/",
            "parse": "/parse/",
            "batch_parse": "/parse/batch/"
        }
    }


@app.get("/health")
async def health_check():
    """Проверка статуса работы API и базы данных"""
    try:
                                                        # 1. ✅ Проверяем соединение с БД
        with connect_db() as session:
            gift_count = session.query(Gift).count()    # 2. ✅ Пытаемся выполнить простой запрос
        
        return {
            "status": "healthy", 
            "timestamp": time.time(),
            "database": "connected",
            "total_gifts": gift_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка подключения к БД: {e}")


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
        raise HTTPException(status_code=500, detail=f"Ошибка при получении данных из БД: {e}")


@app.get("/gifts/{gift_id}", response_model=GiftBase)
async def get_gift_by_id(name: Optional[str] = None):
    """
    Получить информацию о конкретном гифте по ID
    
    - **gift_id**: ID гифта для поиска в базе данных
    """
    try:
        with connect_db() as session:
            gift = session.query(Gift).filter(Gift.name == name).first()
            if not gift:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Гифт с ID {name} не найден в базе данных"
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
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при поиске гифта в БД: {e}"
        )


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
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при парсинге гифта {gift_data.gift_id}: {e}"
        )


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
            print(f"Ошибка при парсинге гифта {gift_id}: {e}")
    
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
    
#     - **task_id**: Идентификатор задачи полученный при запуске парсинга
#     """
#     if task_id not in active_tasks:
#         raise HTTPException(
#             status_code=404, 
#             detail=f"Задача с ID {task_id} не найдена"
#         )
    
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
        async with session.get(f"{config.API_URL}/gifts/" ) as response:
            return await response.json()
    

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )

