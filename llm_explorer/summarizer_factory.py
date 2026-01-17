"""
Factory module for creating summarizer instances.

Provides a simple interface for instantiating OpenRouter-based summarizers.
"""

import logging
from typing import Optional

from llm_explorer.base_summarizer import BaseSummarizer, SummarizationError
from config.env import get_env


def create_summarizer(model: Optional[str] = None) -> BaseSummarizer:
    """
    Create an OpenRouter summarizer instance.

    Note: The returned summarizer uses async methods. Use 'await' when calling
    summarize_article().

    Args:
        model: Optional model identifier (e.g., "meta-llama/llama-3.1-70b-instruct").
               If None, uses OPENROUTER_MODEL env var or default.

    Returns:
        Configured OpenRouterSummarizer instance.

    Raises:
        SummarizationError: If initialization fails.

    Examples:
        # Use default model from env
        summarizer = create_summarizer()
        summary = await summarizer.summarize_article(article_text)

        # Use specific model
        summarizer = create_summarizer(model="google/gemini-flash-1.5")
        summary = await summarizer.summarize_article(article_text)

        # Clean up when done
        await summarizer.close()
    """
    logger = logging.getLogger("SummarizerFactory")

    # Use model from parameter, env var, or default
    if model is None:
        model = get_env("OPENROUTER_MODEL", default=None)

    logger.info(f"Creating OpenRouter summarizer with model: {model or 'default'}")

    try:
        from llm_explorer.openrouter_summarizer import OpenRouterSummarizer

        return OpenRouterSummarizer(model=model)
    except ImportError as e:
        raise SummarizationError(
            f"Failed to import OpenRouterSummarizer: {e}. "
        )
    except Exception as e:
        raise SummarizationError(f"Failed to initialize OpenRouter: {e}")


# Convenience alias
# def create_openrouter_summarizer(
#     model: Optional[str] = None,
# ) -> "OpenRouterSummarizer":
#     """Alias for create_summarizer for clarity."""
#     return create_summarizer(model=model)
