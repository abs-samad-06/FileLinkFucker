# bot/database/db.py

from pymongo import MongoClient, ASCENDING
from bot.config import MONGO_URL


class Database:
    """
    MongoDB wrapper for FileLinkFucker.
    Single shared connection for the entire app.
    """

    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client["filelinkfucker"]

        # Collections
        self.files = self.db["files"]
        self.users = self.db["users"]
        self.passwords = self.db["passwords"]
        self.logs = self.db["logs"]

        self._create_indexes()

    def _create_indexes(self):
        """
        Create indexes for fast lookup and duplicate detection.
        """

        # Files collection
        self.files.create_index([("file_key", ASCENDING)], unique=True)
        self.files.create_index([("content_fingerprint", ASCENDING)])
        self.files.create_index([("user_id", ASCENDING)])
        self.files.create_index([("status", ASCENDING)])

        # Users collection
        self.users.create_index([("user_id", ASCENDING)], unique=True)
        self.users.create_index([("username", ASCENDING)])

        # Passwords collection
        self.passwords.create_index([("file_key", ASCENDING)], unique=True)

        # Logs collection
        self.logs.create_index([("timestamp", ASCENDING)])


# Global DB instance (single source of truth)
db = Database()
