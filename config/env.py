import logging
import os


def get_env(key: str) -> str:
    """
    Args:
        key (str): The key to get the value for.

    Returns:
        str: The value for the key.
    """

    env = os.getenv(key)

    if not env:
        logging.error(f"Environment variable not found: {key}")
        exit(1)

    return env
