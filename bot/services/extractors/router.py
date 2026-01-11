# bot/services/extractors/router.py

from typing import Dict, Tuple, Optional

from pyrogram import Client

from bot.services.extractors.base import BaseExtractor, ExtractResult
from bot.services.extractors.direct import DirectExtractor
from bot.services.extractors.telegram import TelegramExtractor


def identify_source(url: str) -> str:
    """
    Identify source type from URL.
    """
    u = url.lower()
    if "t.me/" in u:
        return "telegram"
    if "terabox" in u:
        return "terabox"
    if "drive.google.com" in u:
        return "gdrive"
    if "mediafire.com" in u:
        return "mediafire"
    if "mega.nz" in u:
        return "mega"
    return "direct"


def get_extractor(
    *,
    url: str,
    app: Optional[Client] = None,
) -> Tuple[str, BaseExtractor]:
    """
    Return (source, extractor_instance).
    """
    source = identify_source(url)

    if source == "telegram":
        if not app:
            raise ValueError("Telegram extractor requires Client")
        return source, TelegramExtractor(url, app)

    if source == "direct":
        return source, DirectExtractor(url)

    # Placeholders for future extractors
    # elif source == "terabox":
    #     return source, TeraboxExtractor(url)
    # elif source == "gdrive":
    #     return source, GDriveExtractor(url)
    # elif source == "mediafire":
    #     return source, MediafireExtractor(url)
    # elif source == "mega":
    #     return source, MegaExtractor(url)

    # Fallback: treat as direct
    return "direct", DirectExtractor(url)


async def analyze_url(
    *,
    url: str,
    app: Optional[Client] = None,
) -> Dict:
    """
    Analyze URL using the appropriate extractor.
    """
    _, extractor = get_extractor(url=url, app=app)
    return await extractor.analyze()


async def extract_url(
    *,
    url: str,
    app: Optional[Client] = None,
) -> ExtractResult:
    """
    Extract URL using the appropriate extractor.
    """
    _, extractor = get_extractor(url=url, app=app)
    return await extractor.extract()
