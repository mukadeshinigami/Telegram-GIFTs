"""
Example configuration for the Telegram bot.

Copy this file to `app/bot/config.py` and fill in real values.
Do NOT commit `app/bot/config.py` to the repository. The repo .gitignore already excludes
`config.py` and `.env` files.

Supported keys (example):
 - BOT_TOKEN: Telegram bot token (string)
 - API_URL: URL of the local FastAPI server (used by the bot if needed)
 - DB_PATH: optional path to SQLite DB file

If you prefer environment variables, use python-dotenv and a local `.env` file instead.
"""

BOT_TOKEN = "your-telegram-bot-token-here"
API_URL = "http://127.0.0.1:8000"
DB_PATH = "/path/to/gifts.db"

# Example: feature toggles / settings
DEBUG = True
