import io
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler


class ColorConsoleFormatter(logging.Formatter):
    """Console format có màu, dễ đọc khi dev."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[1;31m",  # Bold Red
    }
    RESET = "\033[0m"
    GREY = "\033[90m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        ts = datetime.now().strftime("%H:%M:%S")
        level = record.levelname[0]  # I, W, E, D, C
        name = record.name.split(".")[-1]  # short module name
        msg = record.getMessage()
        line = f"{self.GREY}{ts}{self.RESET} {color}{level}{self.RESET} [{name}] {msg}"
        if record.exc_info and record.exc_info[1]:
            line += "\n" + self.formatException(record.exc_info)
        return line


class FileFormatter(logging.Formatter):
    """File format — plain text, không màu, có timestamp đầy đủ."""

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname.ljust(7)
        name = record.name
        msg = record.getMessage()
        line = f"{ts} {level} [{name}] {msg}"
        if record.exc_info and record.exc_info[1]:
            line += "\n" + self.formatException(record.exc_info)
        return line


def setup_logging() -> None:
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)

    # Console handler — có màu, UTF-8
    utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    console = logging.StreamHandler(utf8_stdout)
    console.setFormatter(ColorConsoleFormatter())
    root_logger.addHandler(console)

    # File handler — app.log, xoay vòng 5MB x 3 file
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(FileFormatter())
    root_logger.addHandler(file_handler)

    # Sync-only file — sync.log, chỉ log từ sync module
    sync_handler = RotatingFileHandler(
        os.path.join(log_dir, "sync.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    sync_handler.setFormatter(FileFormatter())
    sync_logger = logging.getLogger("app.services.sync_service")
    sync_logger.addHandler(sync_handler)

    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
