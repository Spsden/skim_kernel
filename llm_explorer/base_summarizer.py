"""
Base abstract class for all summarizer implementations.

This module defines the interface that all summarizers must follow,
enabling easy swapping between different summarization backends
(OpenRouter API, local models, future providers).
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseSummarizer(ABC):
    """
    Abstract base class for summarizer implementations.

    All summarizer backends must inherit from this class and implement
    the summarize_article method.
    """

    def __init__(self) -> None:
        """Initialize the summarizer with configuration."""
        self._logger = None
        self._model_name: str = "unknown"

    @abstractmethod
    async def summarize_article(self, article: str) -> Optional[str]:
        """
        Summarize a single article asynchronously.

        Args:
            article: The full article text to summarize.

        Returns:
            The summarized article text, or None if summarization failed.

        Raises:
            SummarizationError: If summarization fails critically.
        """
        pass

    def get_model_name(self) -> str:
        """Return the name/model identifier of the summarizer."""
        return self._model_name

    def _ensure_string(self, text: Any) -> Optional[str]:
        """Ensure the input is a valid string."""
        if text is None:
            return None
        if isinstance(text, str):
            return text.strip()
        return str(text).strip()


class SummarizationError(Exception):
    """Custom exception for summarization failures."""

    pass
