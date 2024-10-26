import os

from google.cloud import storage
from google.cloud.exceptions import Forbidden, NotFound

from freetrade.logger import logger

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "freetrade-data-eng-hiring")
BLOB_PREFIX = os.getenv("GCS_BLOB_PREFIX", "james_walden")


def upload_to_gcs(
    source_file_path: str, target_file_path: str, retries: int = 3
) -> bool:
    storage_client = storage.Client.create_anonymous_client()
    bucket = storage_client.bucket(BUCKET_NAME)
    target_file_path = os.path.join(BLOB_PREFIX, target_file_path)
    blob = bucket.blob(target_file_path)

    for attempt in range(retries):
        try:
            blob.upload_from_filename(source_file_path)
            logger.info(f"File {source_file_path} uploaded to GCS.")
            return
        except NotFound:
            logger.error(
                f"Bucket {BUCKET_NAME} not found. Please check the bucket name."
            )
            return
        except Forbidden:
            logger.error(f"Permission denied when accessing bucket {BUCKET_NAME}.")
            return
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")

        if attempt < retries - 1:
            logger.info("Retrying upload...")
        else:
            logger.error(f"All {retries} attempts failed. Upload failed.")


def list_gcs_objects(prefix: str, log: bool = False):
    storage_client = storage.Client.create_anonymous_client()
    blobs = storage_client.list_blobs(BUCKET_NAME, prefix=prefix)

    blob_list = [blob.name for blob in blobs]
    if log:
        for blob in blob_list:
            logger.info(blob)
    return blob_list


def validate_presence_of_file(target_file_path: str):
    blobs_list = list_gcs_objects(prefix=BLOB_PREFIX)
    blob_present_in_bucket = os.path.join(BLOB_PREFIX, target_file_path) in blobs_list

    logger.info(f"Blob validation: {blob_present_in_bucket}")
