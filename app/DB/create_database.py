import sqlite3 

database = "gifts.db"

def connect_db():
       
    # The function `connect_db` establishes a connection to a SQLite database and yields the connection
    # for use in a context manager, closing the connection when done.
    
    connect = sqlite3.connect(database)
    
    try:                # Используем генератор т.к будет переход в FASTAPI
        yield connect   #
    finally:            #
        connect.close()
    
def create_database(): 
    
    # The function `create_database` creates a table named `gifts` in a database if it does not already exist.
   
    for connection in connect_db():
        
        cursor = connection.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gifts (
            num INTEGER PRIMARY KEY AUTOINCREMENT,
            id INTEGER,
            name TEXT,
            model TEXT,
            backdrop TEXT,
            symbol TEXT,
            sale_price TEXT
        )
    """)
        connection.commit()
    
def start_database(
    id, name, model, backdrop, symbol, sale_price
):
    
    for connection in connect_db():
        
        cursor = connection.cursor()
        
        cursor.execute(
        """
        INSERT INTO gifts (id, name, model, backdrop, symbol, sale_price)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (id, name, model, backdrop, symbol, sale_price)
        ) 
        connection.commit()

if __name__ == "__main__":
    create_database()       # Тестовый запуск
    start_database(
        id=1,
        name="PlushPepe #1",
        model="Model1",
        backdrop="Blue",
        symbol="PP",
        sale_price="Minted"
    )
