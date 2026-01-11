# bot/services/extractors/telegram.py

import re
from typing import Dict, List

from pyrogram import Client
from pyrogram.errors import ChannelInvalid, ChannelPrivate, MessageIdInvalid

from bot.services.extractors.base import BaseExtractor, ExtractResult


TG_LINK_RE = re.compile(
    r"https?://t\.me/(?P<chat>[^/]+)/(?P<msg_id>\d+)",
    re.IGNORECASE,
)


class TelegramExtractor(BaseExtractor):
    """
    Extractor for public Telegram post/file links.
    """

    def __init__(self, url: str, app: Client):
        super().__init__(url)
        self.app = app

        m = TG_LINK_RE.search(url)
        if not m:
            raise ValueError("Invalid Telegram link format")

        self.chat = m.group("chat")
        self.msg_id = int(m.group("msg_id"))

    async def analyze(self) -> Dict:
        """
        Analyze the Telegram link by fetching the message metadata.
        """
        try:
            msg = await self.app.get_messages(self.chat, self.msg_id)
            if not msg:
                return {"file_count": 0, "is_multi": False, "error": "MESSAGE NOT FOUND"}

            files = self._collect_files(msg)
            return {
                "file_count": len(files),
                "is_multi": len(files) > 1,
                "approx_total_size": sum(f.get("size", 0) or 0 for f in files),
            }

        except (ChannelInvalid, ChannelPrivate):
            return {"file_count": 0, "is_multi": False, "error": "CHANNEL NOT ACCESSIBLE"}
        except MessageIdInvalid:
            return {"file_count": 0, "is_multi": False, "error": "INVALID MESSAGE ID"}
        except Exception as e:
            return {"file_count": 0, "is_multi": False, "error": str(e)}

    async def extract(self) -> ExtractResult:
        """
        Extract file descriptors from the Telegram message.
        """
        try:
            msg = await self.app.get_messages(self.chat, self.msg_id)
            if not msg:
                return self._fail("MESSAGE NOT FOUND")

            files = self._collect_files(msg)
            if not files:
                return self._fail("NO SUPPORTED FILE FOUND")

            return self._ok(files=files, meta={"telegram": True})

        except (ChannelInvalid, ChannelPrivate):
            return self._fail("CHANNEL NOT ACCESSIBLE")
        except MessageIdInvalid:
            return self._fail("INVALID MESSAGE ID")
        except Exception as e:
            return self._fail(str(e))

    # ─────────── HELPERS ───────────

    def _collect_files(self, msg) -> List[Dict]:
        """
        Collect supported file descriptors from a Telegram message.
        """
        files: List[Dict] = []

        tg_file = (
            msg.document
            or msg.video
            or msg.audio
            or msg.voice
        )

        if tg_file:
            files.append(
                {
                    "name": tg_file.file_name or "file.bin",
                    "size": tg_file.file_size,
                    "telegram": {
                        "chat_id": msg.chat.id,
                        "message_id": msg.id,
                    },
                }
            )

        # NOTE:
        # Albums / grouped media can be added later
        # by fetching messages with the same media_group_id.

        return files
