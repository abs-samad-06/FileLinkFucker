# bot/services/extractors/base.py

from abc import ABC, abstractmethod
from typing import Dict, Optional


class ExtractionError(Exception):
    """Raised when extraction fails in a controlled way."""


class ExtractResult:
    """
    Standard extraction result.
    All extractors MUST return this structure.
    """

    def __init__(
        self,
        *,
        source: str,
        success: bool,
        files: Optional[list] = None,
        error: Optional[str] = None,
        meta: Optional[Dict] = None,
    ):
        self.source = source
        self.success = success
        self.files = files or []     # list of file descriptors
        self.error = error
        self.meta = meta or {}


class BaseExtractor(ABC):
    """
    Abstract base class for all link extractors.
    """

    def __init__(self, url: str):
        self.url = url

    @abstractmethod
    async def analyze(self) -> Dict:
        """
        Analyze the URL without downloading.
        Should return:
        - file_count
        - approx_total_size (optional)
        - is_folder / is_multi (bool)
        """
        raise NotImplementedError

    @abstractmethod
    async def extract(self) -> ExtractResult:
        """
        Perform extraction.
        Must return ExtractResult.
        """
        raise NotImplementedError

    # ─────────── HELPERS ───────────

    def _fail(self, reason: str) -> ExtractResult:
        """
        Helper to return a standardized failure.
        """
        return ExtractResult(
            source=self.__class__.__name__,
            success=False,
            error=reason,
        )

    def _ok(self, files: list, meta: Optional[Dict] = None) -> ExtractResult:
        """
        Helper to return a standardized success.
        """
        return ExtractResult(
            source=self.__class__.__name__,
            success=True,
            files=files,
            meta=meta or {},
        )
