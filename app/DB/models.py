from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Gift(Base):
    __tablename__ = 'gifts'

    # Используем `id` как первичный ключ — это соответствует контракту API
    # Значения `id` приходят из внешнего источника (парсер), поэтому
    # отключаем autoincrement, чтобы не перезаписывать внешние ID.
    id = Column(Integer, primary_key=True, autoincrement=False)

    name = Column(String)
    model = Column(String)
    backdrop = Column(String)
    symbol = Column(String)

    # sale_price может быть числом или статусом (например, 'Minted'),
    # поэтому храним его как текст (nullable).
    sale_price = Column(String, nullable=True)

    rarity_score = Column(Float)
    estimated_price = Column(Float)
    # Сохраняем время добавления с дефолтным значением
    date_added = Column(DateTime, default=datetime.utcnow)
