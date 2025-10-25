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

Configuration (local)
---------------------

For local development create a private `app/bot/config.py` with your secrets (bot token, DB path, etc.).
To help, an example file is provided at `app/bot/config.example.py` — copy it and fill in real values:

```bash
cp app/bot/config.example.py app/bot/config.py
# then edit app/bot/config.py and fill BOT_TOKEN, DB_PATH, etc.
```

If you prefer using environment variables, you can use a `.env` file and `python-dotenv`. Either way, do not commit
`app/bot/config.py` or your `.env` file. The repository's `.gitignore` already ignores `config.py` and common `.env` files.

If you accidentally committed secrets, remove them from the git history and rotate the secrets (e.g., regenerate BOT_TOKEN).


