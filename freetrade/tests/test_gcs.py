import json
import os
import tempfile
from unittest.mock import Mock

import pytest
from google.cloud.exceptions import Forbidden, NotFound

from freetrade.gcs import (
    delete_gcs_object,
    get_gcs_object,
    list_gcs_objects,
    upload_to_gcs,
)

TEST_PREFIX = os.environ["GCS_BLOB_PREFIX"]
TEST_TARGET_PATH = os.environ["GCS_BLOB_NAME"]
TEST_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]


@pytest.fixture
def mock_storage_client(mocker):
    mock_blob = Mock()
    mock_blob.exists.return_value = True

    mock_client = Mock()
    mock_client.bucket.return_value = Mock()

    mock_client.bucket.blob.return_value = mock_blob
    mocker.patch(
        "google.cloud.storage.Client.create_anonymous_client", return_value=mock_client
    )
    return mock_client


def test_upload_to_gcs_success(mock_storage_client, mocker):
    mock_bucket = mock_storage_client.bucket.return_value
    mock_blob = mock_bucket.blob.return_value

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"test content")
        temp_file.flush()

    try:
        upload_to_gcs(
            source_file_path=temp_file.name, target_file_path=TEST_TARGET_PATH
        )
        mock_bucket.blob.assert_called_with(os.path.join(TEST_PREFIX, TEST_TARGET_PATH))
        mock_blob.delete.assert_called_once()
        mock_blob.upload_from_filename.assert_called_once_with(temp_file.name)
    finally:

        os.remove(temp_file.name)


def test_upload_to_gcs_bucket_not_found(mock_storage_client, mocker, caplog):
    mock_bucket = mock_storage_client.bucket.return_value
    mock_blob = mock_bucket.blob.return_value

    mock_blob.upload_from_filename.side_effect = NotFound("Bucket not found")

    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(b"test content")
        temp_file.flush()

        upload_to_gcs(
            source_file_path=temp_file.name, target_file_path=TEST_TARGET_PATH
        )

    assert f"Bucket {TEST_BUCKET_NAME} not found" in caplog.text


def test_upload_to_gcs_permission_denied(mock_storage_client, mocker, caplog):
    mock_bucket = mock_storage_client.bucket.return_value
    mock_blob = mock_bucket.blob.return_value

    mock_blob.upload_from_filename.side_effect = Forbidden("Permission denied")

    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(b"test content")
        temp_file.flush()

        upload_to_gcs(
            source_file_path=temp_file.name, target_file_path=TEST_TARGET_PATH
        )

    assert "Permission denied when accessing bucket" in caplog.text


def test_list_gcs_objects(mock_storage_client):
    blob_1_name = f"{TEST_PREFIX}/file1"
    blob_2_name = f"{TEST_PREFIX}/file2"

    mock_blob_1 = Mock(name=blob_1_name)
    mock_blob_1.name = blob_1_name

    mock_blob_2 = Mock(name=blob_2_name)
    mock_blob_2.name = blob_2_name

    mock_blobs = [mock_blob_1, mock_blob_2]

    mock_storage_client.list_blobs.return_value = mock_blobs

    blob_list = list_gcs_objects(prefix=TEST_PREFIX)
    assert blob_list == [blob_1_name, blob_2_name]


def test_get_gcs_object(mock_storage_client):
    mock_bucket = mock_storage_client.bucket.return_value
    mock_blob = mock_bucket.blob.return_value

    result = get_gcs_object(target_file_path=TEST_TARGET_PATH)

    mock_bucket.blob.assert_called_with(os.path.join(TEST_PREFIX, TEST_TARGET_PATH))
    mock_blob.download_to_filename.assert_called_once()
    assert result == []


def test_delete_gcs_object_blob_exists(mock_storage_client):
    mock_bucket = mock_storage_client.bucket.return_value
    mock_blob = mock_bucket.blob.return_value

    delete_gcs_object(target_file_path=TEST_TARGET_PATH)
    mock_blob.delete.assert_called_once()


def test_delete_gcs_object_blob_does_not_exist(mock_storage_client, caplog):
    mock_bucket = mock_storage_client.bucket.return_value
    mock_blob = mock_bucket.blob.return_value
    mock_blob.exists.return_value = False  # Simulate blob does not exist

    delete_gcs_object("test-target-path")
    assert "Blob: test-target-path, does not exist" in caplog.text
