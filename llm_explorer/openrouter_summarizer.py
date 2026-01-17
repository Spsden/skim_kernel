"""
OpenRouter API-based summarizer implementation.

Uses OpenRouter's unified API to access various LLM models for summarization.
Cost-effective approach using quality open-source models.
"""

import asyncio
import logging
import re
from typing import Any, Dict, List, Optional

import aiohttp
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from llm_explorer.base_summarizer import BaseSummarizer, SummarizationError
from config.env import get_env


class OpenRouterSummarizer(BaseSummarizer):
    """
    Summarizer using OpenRouter API.

    OpenRouter provides access to 300+ models through a single OpenAI-compatible API.
    This implementation uses cost-effective models suitable for news summarization.

    Default model: meta-llama/llama-3.1-70b-instruct (excellent quality, low cost)
    Alternative models for different needs:
        - google/gemini-flash-1.5 (faster, cheaper)
        - anthropic/claude-3.5-sonnet (best quality, higher cost)
        - mistralai/mistral-7b-instruct (very cheap, good enough)
    """

    # OpenRouter API endpoint
    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    # Default model (Llama 3.1 70B - excellent quality at ~$0.59/1M tokens)
    DEFAULT_MODEL = "openrouter/auto"

    # Maximum tokens for summary output
    MAX_SUMMARY_TOKENS = 300

    # API request timeout in seconds
    REQUEST_TIMEOUT = 30

    # Maximum retries for failed requests (with exponential backoff)
    MAX_RETRIES = 3

    def __init__(self, model: Optional[str] = None) -> None:
        """
        Initialize OpenRouter summarizer.

        Args:
            model: Optional model identifier. Defaults to Llama 3.1 70B.
                   See https://openrouter.ai/models for available models.
        """
        super().__init__()

        self._logger = logging.getLogger("OpenRouterSummarizer")

        # Load API key from environment
        self._api_key = get_env("OPENROUTER_API_KEY")
        if not self._api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is required but not set"
            )

        self._model = model or get_env("OPENROUTER_MODEL", default=self.DEFAULT_MODEL)
        self._model_name = self._model

        self._logger.info(
            f"OpenRouter summarizer initialized with model: {self._model}"
        )

        # Create aiohttp session (will be created on first use)
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            # Wait a bit for connections to close properly
            await asyncio.sleep(0.25)

    async def summarize_article(self, article: str) -> Optional[str]:
        """
        Summarize an article using OpenRouter API.

        Args:
            article: The article text to summarize.

        Returns:
            Summarized article (50-70 words), or None if failed.

        Raises:
            SummarizationError: If API call fails after retries.
        """
        article = self._ensure_string(article)
        if not article:
            self._logger.warning("Empty article provided for summarization")
            return None

        # For very short articles, check if summarization is needed
        if len(article) < 500:  # ~80 words
            self._logger.info("Article too short, returning as-is")
            return article

        try:
            # Check if article is too long for single API call
            # Most models have 4K-8K input context, Llama 3.1 has 128K
            if len(article) > 25000:  # Conservative character limit (~6-7K tokens)
                return await self._summarize_long_article(article)

            # Single-shot summarization for normal articles
            return await self._summarize_single(article)

        except aiohttp.ClientError as e:
            self._logger.error(f"API request failed: {str(e)}")
            raise SummarizationError(f"Failed to reach OpenRouter API: {str(e)}")
        except Exception as e:
            self._logger.error(f"Summarization failed: {str(e)}")
            return None

    async def _summarize_single(self, article: str) -> Optional[str]:
        """Summarize article in a single API call."""
        prompt = self._build_summarization_prompt(article)

        response = await self._call_api(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional news editor specializing in concise, factual summaries.",
                },
                {"role": "user", "content": prompt},
            ]
        )

        if response:
            print(response)
            summary = self._extract_summary(response)
            self._logger.info(
                f"Summary generated: {len(summary.split())} words from {len(article.split())} words"
            )
            return summary

        return None

    async def _summarize_long_article(self, article: str) -> Optional[str]:
        """
        Summarize a very long article by chunking.

        Strategy:
        1. Split article into chunks
        2. Summarize each chunk concurrently
        3. Synthesize chunk summaries into final summary
        """
        chunks = self._chunk_article(article, chunk_size=3000)
        self._logger.info(f"Long article detected, processing {len(chunks)} chunks")

        # Summarize each chunk concurrently
        chunk_summaries = await asyncio.gather(
            *[self._summarize_chunk(chunk) for chunk in chunks],
            return_exceptions=True
        )

        # Filter out failed chunks
        valid_summaries: List[str] = []
        for i, result in enumerate(chunk_summaries):
            if isinstance(result, Exception):
                self._logger.warning(f"Chunk {i + 1} failed: {result}")
            elif result:
                valid_summaries.append(result)

        if not valid_summaries:
            return None

        # Synthesize all chunks
        if len(valid_summaries) == 1:
            return valid_summaries[0]

        return await self._synthesize_summaries(valid_summaries)

    async def _summarize_chunk(self, chunk: str) -> Optional[str]:
        """Summarize a single chunk of a long article."""
        prompt = self._build_chunk_prompt(chunk)

        response = await self._call_api(
            messages=[
                {
                    "role": "system",
                    "content": "Extract key information from this article segment in 2-3 sentences.",
                },
                {"role": "user", "content": prompt},
            ]
        )

        return self._extract_summary(response) if response else None

    async def _synthesize_summaries(self, summaries: List[str]) -> Optional[str]:
        """Synthesize multiple chunk summaries into one final summary."""
        combined = "\n\n".join(f"- {s}" for s in summaries)
        prompt = f"""Synthesize these segment summaries into a single coherent 50-70 word news summary.
Focus on key facts, events, and outcomes. Remove redundancy.

Segment summaries:
{combined}"""

        response = await self._call_api(
            messages=[
                {
                    "role": "system",
                    "content": "You are a news editor creating a final summary from partial summaries.",
                },
                {"role": "user", "content": prompt},
            ]
        )

        return self._extract_summary(response) if response else None

    @retry(
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _call_api(
        self, messages: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """Call OpenRouter API with retry logic and exponential backoff."""
        session = await self._get_session()

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/wantedbear007/skim_kernel",
        }

        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": self.MAX_SUMMARY_TOKENS,
            "temperature": 0.3,  # Lower temperature for more factual output
            "disable_reasoning": True
        }


        try:
            async with session.post(self.API_URL, headers=headers, json=payload) as response:
                response.raise_for_status()
                return await response.json()

        except aiohttp.ClientResponseError as e:
            if e.status == 429:  # Rate limit
                self._logger.warning(f"Rate limited, will retry with backoff")
                raise  # Let tenacity handle retry with backoff
            else:
                self._logger.error(f"HTTP error: {e.status}")
                raise

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            self._logger.warning(f"Request failed: {str(e)}, will retry with backoff")
            raise  # Let tenacity handle retry with backoff

    def _extract_summary(self, response: Dict[str, Any]) -> Optional[str]:
        """Extract summary text from API response."""
        try:
            return response["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as e:
            self._logger.error(f"Failed to parse API response: {str(e)}")
            return None

    def _build_summarization_prompt(self, article: str) -> str:
        """Build the main summarization prompt."""
        return f"""Create a concise 50-70 word summary of this news article.

Requirements:
- Focus on key facts: who, what, when, where, why
- Use neutral, objective tone
- No opinions or speculation
- Remove redundancy

Article:
{article}"""

    def _build_chunk_prompt(self, chunk: str) -> str:
        """Build prompt for processing article chunks."""
        return f"""Extract and condense key information from this segment into 2-3 sentences.
Focus on facts, names, dates, places, and events.

Segment:
{chunk}"""

    def _chunk_article(self, article: str, chunk_size: int = 3000) -> List[str]:
        """Split article into chunks while preserving sentence boundaries."""
        # Fixed regex - removed double << that was causing syntax error
        sentences = re.split(r"(?<=[.!?])\s+", article)

        chunks: List[str] = []
        current_chunk: List[str] = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if current_length + sentence_length > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks


# Factory function for easy instantiation
async def create_openrouter_summarizer(model: Optional[str] = None) -> OpenRouterSummarizer:
    """
    Factory function to create an OpenRouter summarizer.

    Args:
        model: Optional model identifier.

    Returns:
        Configured OpenRouterSummarizer instance.

    Example:
        summarizer = await create_openrouter_summarizer()
        summary = await summarizer.summarize_article(article_text)
    """
    return OpenRouterSummarizer(model=model)
