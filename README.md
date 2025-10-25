A short and lightweight Telegram bot/script for working with GIF/"gifts" in chats (sending, storing and managing).


Note:
- This is my first pet project — I created it to learn and showcase how these technologies work together.

Requirements:

    Python 3.8+
    Libraries: all listed in requirements.txt

Short:
Libraries: specified in requirements.txt
Small preview:

    🔹 aiohttp — asynchronous HTTP client/server (uploading/sending GIFs in the background).
    ⚡ fastapi — fast web framework for APIs (if an HTTP interface is needed).
    🚀 uvicorn — ASGI server to run FastAPI/asynchronous apps.
    🧩 pydantic — data validation/parsing and configuration models.
    🧰 python-dotenv — load configuration from .env (BOT_TOKEN, etc.).
    🔁 requests — simple synchronous HTTP client (for external requests).
    🗄️ SQLAlchemy — ORM for working with the database (storing metadata).
    🔎 beautifulsoup4 — HTML parsing (extracting data from pages if needed).
    🔗 yarl / multidict / frozenlist — utilities for URL handling and async requests (helpers for aiohttp).
    
---
Quick start:

 - Fill in the bot token (BOT_TOKEN) and other variables.
 - Install dependencies: pip install -r requirements.txt
 - Run the API server: app.main.py
 - Run the Telegram bot: app.bot.main.py
 - Finish 🤍🍭


