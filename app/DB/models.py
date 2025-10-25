from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Gift(Base):
    __tablename__ = 'gifts'
    
    num = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(Integer)
    name = Column(String)
    model = Column(String)
    backdrop = Column(String)
    symbol = Column(String)
    sale_price = Column(Integer)
    
    rarity_score = Column(Float)
    estimated_price = Column(Float)
    date_added = Column(DateTime)
