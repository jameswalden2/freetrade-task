import os
import time

import requests
from requests import HTTPError

from freetrade.logger import logger

RETRIES = os.getenv("REQUEST_RETRIES", 3)
BACKOFF_FACTOR = os.getenv("REQUEST_BACKOFF_FACTOR", 1)


def get_request(url: str) -> dict:

    for attempt in range(RETRIES):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            logger.error(f"HTTP error: {e}")
            break
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < RETRIES - 1:
                wait_time = BACKOFF_FACTOR * (2**attempt)
                logger.info(f"Retrying in {wait_time:.1f} seconds...")
                time.sleep(wait_time)
            else:
                logger.error("All retry attempts failed.")

    return None
