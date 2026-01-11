# bot/services/links.py

from typing import Dict
from urllib.parse import quote

from bot.config import BASE_URL
from bot.database.db import db
from bot.services.storage import mark_access
from bot.utils.passwords import is_protected


def build_links(file_key: str) -> Dict[str, str]:
    """
    Build all public-facing links for a file_key.
    NOTE:
    - Actual password gate is enforced at API endpoints.
    """
    # URL-safe key
    safe_key = quote(file_key)

    return {
        "download": f"{BASE_URL}/d/{safe_key}",
        "stream": f"{BASE_URL}/s/{safe_key}",
        "telegram": f"{BASE_URL}/tg/{safe_key}",
    }


def get_links_if_allowed(file_key: str) -> Dict[str, str]:
    """
    Return links if file exists and is not nuked.
    Does NOT bypass password; endpoints will enforce it.
    """
    doc = db.files.find_one(
        {"file_key": file_key, "status": {"$ne": "nuked"}}
    )
    if not doc:
        return {}

    # Increment access stats (request intent)
    mark_access(file_key)

    return build_links(file_key)


def file_requires_password(file_key: str) -> bool:
    """
    Check if file is password-protected.
    """
    return is_protected(file_key)
