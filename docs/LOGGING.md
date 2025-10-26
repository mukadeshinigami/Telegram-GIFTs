# Logging in Telegram-GIFTs

This project configures logging centrally to make debugging and monitoring easier.

Location
- `app/logging_config.py` — initialization and helpers (`init_logging`, `get_logger`, `new_error_id`).

Behavior
- Console: logs are written to stdout for real-time visibility.
- File: rotating log file `logs/app.log` (10 MB per file, 5 backups).
- On exceptions in API endpoints a short `error_id` is generated and returned to the client; the full traceback is written to the logs with that id.

How to use
- In modules import a logger with:

  from app.logging_config import get_logger
  logger = get_logger(__name__)

- Use `logger.debug/info/warning/error/exception()` instead of `print()`.

Running
- No special steps are required. Logs directory is created automatically when the app imports `app.logging_config`.

Production notes
- For production, consider increasing log rotation retention, shipping logs to a central system (ELK, Loki, etc.), or integrating structured JSON logging.
- Protect log files containing potentially sensitive data — rotate and secure file permissions appropriately.
