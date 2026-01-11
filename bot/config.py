# bot/config.py

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


def _get_env(name: str, default=None, required: bool = False):
    value = os.getenv(name, default)
    if required and value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


# ─────────── TELEGRAM ───────────
API_ID = int(_get_env("API_ID", required=True))
API_HASH = _get_env("API_HASH", required=True)
BOT_TOKEN = _get_env("BOT_TOKEN", required=True)

# ─────────── OWNER / ADMIN ───────────
OWNER_ID = int(_get_env("OWNER_ID", required=True))

# ─────────── DATABASE ───────────
MONGO_URL = _get_env("MONGO_URL", required=True)

# ─────────── SERVER / LINKS ───────────
BASE_URL = _get_env("BASE_URL", required=True)
API_HOST = _get_env("API_HOST", "0.0.0.0")
API_PORT = int(_get_env("API_PORT", 8000))

# ─────────── CHANNELS ───────────
FSUB_CHANNELS = [
    ch.strip()
    for ch in _get_env("FSUB_CHANNELS", "").split(",")
    if ch.strip()
]

STORAGE_CHANNEL_ID = int(_get_env("STORAGE_CHANNEL_ID", required=True))
LOG_CHANNEL_ID = int(_get_env("LOG_CHANNEL_ID", required=True))

# ─────────── LIMITS / MODES ───────────
AUTO_BATCH_LIMIT = int(_get_env("AUTO_BATCH_LIMIT", 5))
MIN_PASSWORD_LENGTH = int(_get_env("MIN_PASSWORD_LENGTH", 6))
MAX_PASSWORD_LENGTH = int(_get_env("MAX_PASSWORD_LENGTH", 64))

# ─────────── CLEANUP ───────────
AUTO_CLEANUP_DAYS = int(_get_env("AUTO_CLEANUP_DAYS", 30))
DISK_USAGE_LIMIT = int(_get_env("DISK_USAGE_LIMIT", 85))


# ─────────── DEBUG (optional) ───────────
DEBUG = _get_env("DEBUG", "false").lower() == "true"
