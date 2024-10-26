import json
import os
import tempfile

from google.cloud import storage
from google.cloud.exceptions import Forbidden, NotFound

from freetrade import BLOB_PREFIX, BUCKET_NAME
from freetrade.logger import logger


def upload_to_gcs(source_file_path: str, target_file_path: str, retries: int = 3):
    """Save file to gcs.

    Args:
        source_file_path (str): file path of file to upload.
        target_file_path (str): name of blob in gcs.
        retries (int): number of retries to attempt.
    """
    storage_client = storage.Client.create_anonymous_client()
    bucket = storage_client.bucket(BUCKET_NAME)
    target_file_path = os.path.join(BLOB_PREFIX, target_file_path)
    blob = bucket.blob(target_file_path)
    if blob.exists():
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


def list_gcs_objects(prefix: str | None = None, log: bool = False) -> list:
    """List gcs objects with a given prefix.

    Args:
        prefix (str | None): prefix of objects.
        log (bool): log each object to console, default False.

    Returns:
        list: list of gcs objects with given prefix.
    """
    storage_client = storage.Client.create_anonymous_client()
    blobs = storage_client.list_blobs(BUCKET_NAME, prefix=prefix)
    blob_list = [blob.name for blob in blobs]
    if log:
        for blob in blob_list:
            logger.info(blob)
    return blob_list


def get_gcs_object(target_file_path: str) -> list[dict]:
    """List gcs objects with a given prefix.

    Args:
        target_file_path (str): object name to get from gcs.

    Returns:
        list[dict]: list of data contained in object.
    """
    storage_client = storage.Client.create_anonymous_client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(os.path.join(BLOB_PREFIX, target_file_path))

    with tempfile.NamedTemporaryFile(mode="w+") as f:
        blob.download_to_filename(f.name)

        data = [json.loads(line) for line in f]

    return data


def delete_gcs_object(target_file_path: str):
    """Delete gcs object at path.

    Args:
        target_file_path (str): object name to delete from gcs.
    """
    storage_client = storage.Client.create_anonymous_client()
    bucket = storage_client.bucket(BUCKET_NAME)

    blob = bucket.blob(target_file_path)

    if blob.exists():
        logger.info(f"Deleting blob: {target_file_path}")
        blob.delete()
    else:
        logger.info(f"Blob: {target_file_path}, does not exist")
