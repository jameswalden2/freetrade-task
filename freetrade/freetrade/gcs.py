import json
import os
import tempfile

from google.cloud import storage
from google.cloud.exceptions import Forbidden, NotFound

from freetrade import BLOB_PREFIX, BUCKET_NAME
from freetrade.logger import logger


def upload_to_gcs(
    source_file_path: str, target_file_path: str, retries: int = 3
) -> bool:
    storage_client = storage.Client.create_anonymous_client()
    bucket = storage_client.bucket(BUCKET_NAME)
    target_file_path = os.path.join(BLOB_PREFIX, target_file_path)

    blob = bucket.blob(target_file_path)

    # first delete blob if exists
    if blob.exists():
        # don't need to catch NotFound because check existed
        logger.info(f"Deleting blob: {target_file_path}")
        blob.delete()
    else:
        logger.info(f"Blob: {target_file_path}, does not exist")

    for attempt in range(retries):
        try:
            blob.upload_from_filename(source_file_path)
            logger.info(
                f"File {source_file_path} uploaded to GCS at: {target_file_path}."
            )
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

    print(blob_list)
    return blob_list


def get_gcs_object(target_file_path: str) -> list[dict]:
    storage_client = storage.Client.create_anonymous_client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(os.path.join(BLOB_PREFIX, target_file_path))

    with tempfile.NamedTemporaryFile(mode="w+") as f:
        blob.download_to_filename(f.name)

        data = [json.loads(line) for line in f]

    return data


def delete_gcs_object(target_file_path: str):
    storage_client = storage.Client.create_anonymous_client()
    bucket = storage_client.bucket(BUCKET_NAME)

    blob = bucket.blob(target_file_path)

    # first delete blob if exists
    if blob.exists():
        # don't need to catch NotFound because check existed
        logger.info(f"Deleting blob: {target_file_path}")
        blob.delete()
    else:
        logger.info(f"Blob: {target_file_path}, does not exist")


# blobs_list = list_gcs_objects(prefix=BLOB_PREFIX)
# blob_present_in_bucket = os.path.join(BLOB_PREFIX, target_file_path) in blobs_list

# logger.info(f"Blob validation: {blob_present_in_bucket}")
