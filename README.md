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

Install as a package (recommended for development)
-----------------------------------------------

Installing the project into your virtualenv makes imports like `import app...` work reliably.

From the repository root:

```bash
# create and activate a virtualenv (if you haven't already)
python -m venv .venv
source .venv/bin/activate

# install runtime deps
pip install -r requirements.txt

# install this package in editable mode so imports resolve and you can make changes in-place
pip install -e .
```

After that you can run the app via uvicorn:

```bash
uvicorn app.main:app --reload
```

Logging
-------

This project uses a centralized logging configuration located at `app/logging_config.py`.

- Logs are written to console and to a rotating file at `logs/app.log` (created automatically).
- The logging is initialized when the `app` package is imported. If you run modules directly, they also initialize logging.
- When an internal server error occurs, the API returns a short error id (e.g. `id=abcd1234`) and the full traceback is recorded in the logs — use the id to correlate client errors with server-side logs.

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


