import requests, time
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import logging

from app.logging_config import get_logger

logger = get_logger(__name__)

# Импортируем модули БД относительно пакета app
from ..DB.create_database import start_database, create_database


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}

def parse_fragment(
    gift_id: int, 
    user_selection_gifts: str
    ):  
    
    """
    Парсит данные о гифте по ID с fragment.com
    """

    url = f"https://fragment.com/gift/{user_selection_gifts}-{gift_id}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except RequestException as e:
        logger.warning("Ошибка запроса %s: %s", url, e)
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    name_gift_id_tag = soup.find(class_="tm-section-header-title")
    name_gift_id = name_gift_id_tag.text.strip() if name_gift_id_tag else None
    
    sale_price_teg = soup.find(class_="table-cell-value tm-value icon-before icon-ton")
    sale_price = sale_price_teg.text.replace("TON", "").strip() if sale_price_teg else "Minted"
    
    tags = soup.find_all("a", class_="table-cell-value-link")
    if len(tags) < 3 or not all(tags[i].text.strip() for i in range(3)):
        logger.info("Пропускаем Gift #%s — недостаточно данных", gift_id)
        return None
    
    model = tags[0].text.strip()
    backdrop = tags[1].text.strip()
    symbol = tags[2].text.strip()
    
    gift_data = {
        "id": gift_id,
        "name": name_gift_id,
        "model": model,
        "backdrop": backdrop,
        "symbol": symbol,
        "sale_price": sale_price
    }
    
    try:
        create_database()
        start_database(
            id=gift_id,
            name=name_gift_id,
            model=model,
            backdrop=backdrop,
            symbol=symbol,
            sale_price=sale_price,
        )
    except Exception as e:
        logger.exception("Ошибка при сохранении Gift #%s в БД: %s", gift_id, e)
        return None
    else:
        # Возвращаем собранные данные после успешного сохранения
        return gift_data
    
if __name__ == "__main__":
    # Для тестирования можно задать значение по умолчанию
    for num in range(1, 10):
        data = parse_fragment(num, "lootbag")  # Передаем оба параметра
        if data:
            for key, value in data.items():
                logger.info("%s: %s", key, value)
        time.sleep(1)

    # конец модуля