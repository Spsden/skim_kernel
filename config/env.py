import logging
import os
from typing import Optional


def get_env(key: str, default: Optional[str] = None, required: bool = False) -> str:
    """
    Get environment variable value with optional default and required checking.

    Args:
        key (str): The environment variable key.
        default: Default value if env var is not set. Only used if required=False.
        required: If True, raise error when env var is not set (default: False).

    Returns:
        str: The environment variable value, or default if not set and not required.

    Raises:
        SystemExit: If required=True and env var is not found.
    """
    env = os.getenv(key)

    if not env:
        if default is not None:
            return default
        if required:
            logging.error(f"Required environment variable not found: {key}")
            exit(1)
        # Return empty string if not required and no default
        return ""

    return env
