# bot/utils/identity.py

import hashlib
import random
import string
from typing import Optional


def generate_fingerprint(
    *,
    file_unique_id: Optional[str] = None,
    source_url: Optional[str] = None,
) -> str:
    """
    Generate a stable fingerprint for a file or link.
    Priority:
    - Telegram file_unique_id (best)
    - Source URL (fallback)
    """

    base = ""

    if file_unique_id:
        base = file_unique_id
    elif source_url:
        base = source_url
    else:
        raise ValueError("Either file_unique_id or source_url is required")

    return hashlib.sha256(base.encode()).hexdigest()


def generate_file_key(length: int = 10) -> str:
    """
    Generate a short, human-usable file key.
    Example: a9f3kqz8tm
    """
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choices(alphabet, k=length))


def generate_secure_key(
    *,
    fingerprint: str,
    length: int = 10,
) -> str:
    """
    Generate a deterministic + random mixed key.
    Uses fingerprint hash + random salt.
    """

    hash_part = fingerprint[:6]
    salt = generate_file_key(length=length - 6)
    return f"{hash_part}{salt}"
