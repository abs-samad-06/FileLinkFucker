# bot/utils/passwords.py

import re
import hashlib
from typing import Tuple

from bot.config import MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH
from bot.database.db import db


# ─────────── RULES ───────────

_PASSWORD_REGEX = re.compile(r"^[\w@#\$%\-\+!]+$")


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password rules.
    Allowed examples:
    - 123456
    - Sam123
    - @Samad
    """

    if not password:
        return False, "Password cannot be empty"

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Minimum length is {MIN_PASSWORD_LENGTH}"

    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Maximum length is {MAX_PASSWORD_LENGTH}"

    if not _PASSWORD_REGEX.match(password):
        return False, "Invalid characters in password"

    return True, "OK"


# ─────────── HASHING ───────────

def _hash(password: str) -> str:
    """
    Hash password using SHA-256.
    """
    return hashlib.sha256(password.encode()).hexdigest()


# ─────────── DB OPERATIONS ───────────

def set_password(file_key: str, password: str) -> None:
    """
    Set or overwrite password for a file_key.
    """
    pwd_hash = _hash(password)

    db.passwords.update_one(
        {"file_key": file_key},
        {
            "$set": {
                "password_hash": pwd_hash,
                "protected": True,
            }
        },
        upsert=True,
    )


def is_protected(file_key: str) -> bool:
    """
    Check if a file is password-protected.
    """
    doc = db.passwords.find_one({"file_key": file_key})
    return bool(doc and doc.get("protected"))


def verify_password(file_key: str, password: str) -> bool:
    """
    Verify password for a file_key.
    """
    doc = db.passwords.find_one({"file_key": file_key})
    if not doc or not doc.get("protected"):
        return True  # Not protected → always allowed

    return doc.get("password_hash") == _hash(password)


def remove_password(file_key: str) -> None:
    """
    Remove password protection (ADMIN use).
    """
    db.passwords.delete_one({"file_key": file_key})
