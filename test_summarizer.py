"""
Quick test script for the OpenRouter summarizer.
Tests async functionality without needing the full queue pipeline.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from llm_explorer.openrouter_summarizer import OpenRouterSummarizer


# Sample article for testing
TEST_ARTICLE = """
Apple Inc. unveiled its latest lineup of MacBook Pro laptops today, featuring the new M3 chip family.
The company claims the new chips deliver up to 50% faster performance compared to the previous generation.
The MacBook Pro models will be available in 14-inch and 16-inch configurations, with prices starting at $1,599.
Pre-orders begin today, with availability in stores starting next week. The announcement comes as Apple
faces increasing competition in the laptop market from rivals like Dell and HP. Analysts believe the new
release could help Apple regain market share in the premium laptop segment.
"""


async def test_summarizer():
    """Test the OpenRouter summarizer with a sample article."""

    print("=" * 60)
    print("OpenRouter Summarizer Test")
    print("=" * 60)

    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_api_key_here":
        print("\nERROR: OPENROUTER_API_KEY not set in .env file!")
        print("Get your key from: https://openrouter.ai/keys")
        return

    try:
        # Initialize summarizer
        print("\n1. Initializing OpenRouter summarizer...")
        summarizer = OpenRouterSummarizer()
        print(f"   Model: {summarizer.get_model_name()}")

        # Test short article
        print("\n2. Testing with short article (< 500 chars)...")
        short_article = "This is a very short article that should be returned as-is."
        result = await summarizer.summarize_article(short_article)
        print(f"   Result: {result}")

        # Test normal article
        print("\n3. Testing with normal article...")
        result = await summarizer.summarize_article(TEST_ARTICLE)
        if result:
            print(f"   Summary ({len(result.split())} words):")
            print(f"   {result}")
        else:
            print("   ERROR: Summarization returned None")

        # Test long article (triggers chunking)
        print("\n4. Testing with long article (chunking)...")
        long_article = TEST_ARTICLE * 50  # ~4000 chars
        result = await summarizer.summarize_article(long_article)
        if result:
            print(f"   Summary ({len(result.split())} words):")
            print(f"   {result}")
        else:
            print("   ERROR: Long article summarization returned None")

        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)

    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
    except Exception as e:
        print(f"\nTest Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        if 'summarizer' in locals():
            await summarizer.close()
            print("\nSummarizer session closed.")


if __name__ == "__main__":
    asyncio.run(test_summarizer())
