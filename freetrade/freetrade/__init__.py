import os
import random
import string
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv("./.env.freetrade")

RUN_TIMESTAMP = datetime.now(timezone.utc)
RUN_TIMESTAMP_STR = RUN_TIMESTAMP.strftime("%Y_%m_%d__%H_%M_%S")

RUN_UNIQUE_ID = "".join(
    random.choices(
        string.ascii_uppercase + string.digits + string.ascii_lowercase, k=10
    )
)

RUN_IDENTIFIER = f"{RUN_TIMESTAMP_STR}_{RUN_UNIQUE_ID}"

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "freetrade-data-eng-hiring")
BLOB_PREFIX = os.getenv("GCS_BLOB_PREFIX", "james_walden")
BLOB_NAME = os.getenv("GCS_BLOB_NAME", "data_engineering_task.json")

RETRIES = os.getenv("REQUEST_RETRIES", 3)
BACKOFF_FACTOR = os.getenv("REQUEST_BACKOFF_FACTOR", 1)

FAKER_QUANTITY = os.getenv("FAKER_QUANTITY", 10)
if FAKER_QUANTITY <= 0:
    raise ValueError("FAKER_QUANTITY must be greater than 0.")
