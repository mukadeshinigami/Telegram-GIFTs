from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from datetime import datetime
from models import Base, Gift  # Импортируем модель из вашего файла model.py

DATABASE_URL = "sqlite:///gifts.db"  # URL вашей базы данных SQLite
engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

@contextmanager
def connect_db():
       
    # Context manager for database session.
    
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    
def create_database(): 
  
    # Create the database and tables.
    
    Base.metadata.create_all(engine)
    
def start_database(
    id, name, model, backdrop, symbol, sale_price
):
    
    with connect_db() as session:
        
        exiting_gift = session.query(Gift).filter_by(name=name).first()
        if exiting_gift:
            print(f"Gift с именем {name} уже существует.")
            return 
        
        new_gift = Gift(
            id=id,
            name=name,
            model=model,
            backdrop=backdrop,
            symbol=symbol,
            sale_price=sale_price,
            rarity_score=None,  
            estimated_price=None,
            date_added=datetime.now()  # Автоматически устанавливаем текущее время
        )
        session.add(new_gift)
    print(f"Добавлен новый Gift: {name}")
if __name__ == "__main__":
    
    create_database()       # Тестовый запуск
    start_database(
        id=999,
        name="PlushPepe #1",
        model="Model1",
        backdrop="Blue",
        symbol="PP",
        sale_price="Minted"
    )
