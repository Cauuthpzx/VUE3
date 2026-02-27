"""
Logging configuration — 7 tầng logging với chấm tròn màu sắc.

7 Levels (thấp → cao):
  ⚪ TRACE    (5)  — chi tiết nhất: HTTP raw, SQL query, biến nội bộ
  🔵 DEBUG   (10)  — thông tin debug: response code, payload size
  🟢 INFO    (20)  — hoạt động bình thường: khởi động, request, kết quả
  🟡 SUCCESS (25)  — hoàn thành quan trọng: sync xong, login thành công
  🟠 WARNING (30)  — cảnh báo: retry, timeout, dữ liệu lạ
  🔴 ERROR   (40)  — lỗi: request fail, DB error, cookie hết hạn
  ⛔ CRITICAL(50)  — sập hệ thống: DB mất kết nối, app crash
"""

import io
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

# ── Custom levels ────────────────────────────────────────────────────────────

TRACE = 5
SUCCESS = 25

logging.addLevelName(TRACE, "TRACE")
logging.addLevelName(SUCCESS, "SUCCESS")


def _trace(self, msg, *args, **kwargs):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, msg, args, **kwargs)


def _success(self, msg, *args, **kwargs):
    if self.isEnabledFor(SUCCESS):
        self._log(SUCCESS, msg, args, **kwargs)


logging.Logger.trace = _trace
logging.Logger.success = _success

# ── ANSI color codes ─────────────────────────────────────────────────────────

_RST = "\033[0m"
_GREY = "\033[90m"
_DIM = "\033[2m"
_BOLD = "\033[1m"

# Dot + Level name colors
_LEVELS = {
    "TRACE":    {"dot": "\033[37m●",  "name": "\033[37mTRACE   "},        # White dot, white name
    "DEBUG":    {"dot": "\033[34m●",  "name": "\033[34mDEBUG   "},        # Blue dot, blue name
    "INFO":     {"dot": "\033[32m●",  "name": "\033[32mINFO    "},        # Green dot, green name
    "SUCCESS":  {"dot": "\033[33m●",  "name": "\033[1;33mSUCCESS "},      # Yellow dot, bold yellow name
    "WARNING":  {"dot": "\033[38;5;208m●", "name": "\033[38;5;208mWARNING "},  # Orange dot, orange name
    "ERROR":    {"dot": "\033[31m●",  "name": "\033[31mERROR   "},        # Red dot, red name
    "CRITICAL": {"dot": "\033[1;31m●", "name": "\033[1;31mCRITICAL"},     # Bold red dot, bold red name
}


class ColorConsoleFormatter(logging.Formatter):
    """
    Console format có màu với chấm tròn (●) và tên level đầy đủ.

    Output:
      HH:MM:SS 🟢 INFO     [module] message
      HH:MM:SS 🔴 ERROR    [module] message
    """

    def format(self, record: logging.LogRecord) -> str:
        lvl = _LEVELS.get(record.levelname, _LEVELS["INFO"])
        ts = datetime.now().strftime("%H:%M:%S")
        name = record.name.split(".")[-1]
        msg = record.getMessage()

        line = (
            f"{_GREY}{ts}{_RST} "
            f"{lvl['dot']}{_RST} "
            f"{lvl['name']}{_RST} "
            f"{_DIM}[{name}]{_RST} "
            f"{msg}"
        )

        if record.exc_info and record.exc_info[1]:
            line += "\n" + self.formatException(record.exc_info)
        return line


class FileFormatter(logging.Formatter):
    """File format — plain text, không màu, có timestamp đầy đủ."""

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname.ljust(8)
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
    root_logger.setLevel(TRACE)  # Cho phép mọi level đi qua, handler tự filter

    # ── Console handler — có màu, UTF-8 ──────────────────────────────────
    utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    console = logging.StreamHandler(utf8_stdout)
    console.setLevel(logging.DEBUG)  # Console hiển thị từ DEBUG trở lên
    console.setFormatter(ColorConsoleFormatter())
    root_logger.addHandler(console)

    # ── File handler — app.log, xoay vòng 5MB x 3 file ──────────────────
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(TRACE)  # File ghi tất cả
    file_handler.setFormatter(FileFormatter())
    root_logger.addHandler(file_handler)

    # ── Sync-only file — sync.log ────────────────────────────────────────
    sync_handler = RotatingFileHandler(
        os.path.join(log_dir, "sync.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    sync_handler.setFormatter(FileFormatter())
    sync_logger = logging.getLogger("app.services.sync_service")
    sync_logger.addHandler(sync_handler)

    # ── Tắt bớt noise ────────────────────────────────────────────────────
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("hpack").setLevel(logging.WARNING)
