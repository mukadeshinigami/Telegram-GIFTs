import logging
import logging.config
import os
from logging.handlers import RotatingFileHandler
import uuid

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def init_logging(level: str = "INFO"):
    """Initialize structured logging for the application.

    Configures a console handler and a rotating file handler. Call this early
    (at package import or application startup).
    """
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    logger = logging.getLogger()
    if logger.handlers:
        # assume already configured
        return

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    console = logging.StreamHandler()
    console.setLevel(getattr(logging, level.upper(), logging.INFO))
    console.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    logger.addHandler(console)

    file_path = os.path.join(LOG_DIR, "app.log")
    file_handler = RotatingFileHandler(file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    file_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    logger.addHandler(file_handler)


def new_error_id() -> str:
    """Return a short unique id for correlating logged errors to external responses."""
    return uuid.uuid4().hex[:8]


def get_logger(name: str = __name__):
    return logging.getLogger(name)
