# bot/services/extractors/direct.py

import aiohttp
from typing import Dict

from bot.services.extractors.base import BaseExtractor, ExtractResult


class DirectExtractor(BaseExtractor):
    """
    Extractor for direct HTTP/HTTPS file links.
    """

    async def analyze(self) -> Dict:
        """
        Analyze the direct link using HEAD request.
        Returns file_count=1 if reachable.
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.head(self.url, allow_redirects=True, timeout=15) as resp:
                    if resp.status >= 400:
                        return {
                            "file_count": 0,
                            "is_multi": False,
                            "error": f"HTTP {resp.status}",
                        }

                    size = resp.headers.get("Content-Length")
                    return {
                        "file_count": 1,
                        "approx_total_size": int(size) if size and size.isdigit() else None,
                        "is_multi": False,
                    }
            except Exception as e:
                return {
                    "file_count": 0,
                    "is_multi": False,
                    "error": str(e),
                }

    async def extract(self) -> ExtractResult:
        """
        Extraction for direct links does NOT download here.
        It just returns a file descriptor with the direct URL.
        """
        # Try to infer filename from URL
        name = self.url.split("?")[0].rstrip("/").split("/")[-1] or "file.bin"

        # Best-effort HEAD to get size/type
        size = None
        content_type = None

        async with aiohttp.ClientSession() as session:
            try:
                async with session.head(self.url, allow_redirects=True, timeout=15) as resp:
                    if resp.status >= 400:
                        return self._fail(f"HTTP {resp.status}")

                    size_hdr = resp.headers.get("Content-Length")
                    if size_hdr and size_hdr.isdigit():
                        size = int(size_hdr)
                    content_type = resp.headers.get("Content-Type")
            except Exception as e:
                return self._fail(str(e))

        file_desc = {
            "name": name,
            "size": size,
            "content_type": content_type,
            "download_url": self.url,
        }

        return self._ok(files=[file_desc], meta={"direct": True})
