import json
import os
import tempfile
from typing import Any

from pydantic import ValidationError

from freetrade.api_handler import get_request
from freetrade.gcs import list_gcs_objects, upload_to_gcs, validate_presence_of_file
from freetrade.logger import LOGS_FILE_NAME, logger
from freetrade.models import FakerData, FakerResponse
from freetrade.setup import RUN_TIMESTAMP_STR, RUN_UNIQUE_ID

BLOB_NAME = os.getenv("GCS_BLOB_NAME", "dev/data_engineering_task.json")


FAKER_QUANTITY = os.getenv("FAKER_QUANTITY", 10)
if FAKER_QUANTITY <= 0:
    raise ValueError("FAKER_QUANTITY must be greater than 0.")


def get_faker_data(quantity: int) -> dict | None:
    """Makes a get request for new faker data.

    Args:
        quantity (int): the quantity of users to retrieve.

    Returns:
        dict | None: A dictionary response or None if the request fails.
    """
    FAKER_URL = f"https://fakerapi.it/api/v1/users?_quantity={quantity}"

    return get_request(url=FAKER_URL)


def validate_response(
    response: dict,
) -> tuple[list[FakerData] | None, list[str] | None]:
    """Validate the response data against the FakerResponse model.

    Args:
        response (dict): A dictionary containing the response data
        to validate against the FakerResponse model.

    Returns:
        tuple:
            A tuple containing:
            - list[FakerData] | None: A list of validated FakerData instances
              if validation is successful, or None if validation fails.
            - list[str] | None: A list of error messages if validation
              fails, or None if validation is successful.
    """
    try:
        response: FakerResponse = FakerResponse(**response)
        return response.data, None
    except ValidationError as e:
        logger.error(f"Encountered {e.error_count()} errors trying to validate data.")
        error_strs = [json.dumps(x) for x in e.errors()]
        for error in error_strs:
            logger.info(json.dumps(error))

    return None, error_strs


def transform_response(data: list[FakerData]):
    for x in data:
        # add run id
        x.pipeline_id = RUN_UNIQUE_ID
        # add run timestamp
        x.pipeline_timestamp = RUN_TIMESTAMP_STR

    return data


def load_data_to_gcs(data: list[FakerData], target_file_path: str) -> bool:

    data_as_json = [x.model_dump_json(serialize_as_any=True) for x in data]

    try:
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w") as temp_file:
            for data in data_as_json:
                json.dump(data, temp_file)
                temp_file.write("\n")
            upload_to_gcs(
                source_file_path=temp_file.name,
                target_file_path=target_file_path,
            )
        return True
    except Exception as e:
        logger.error(e)
        return False


def save_failed_response(response: dict, errors: list[str]):

    failed_response = {"errors": errors, "response": response}

    target_file_path = f"failed/{RUN_UNIQUE_ID}_{RUN_TIMESTAMP_STR}_response.json"

    with tempfile.NamedTemporaryFile(suffix=".json", mode="w") as temp_file:
        json.dump(failed_response, temp_file)
        upload_to_gcs(
            source_file_path=temp_file.name,
            target_file_path=target_file_path,
        )


def save_logs():
    upload_to_gcs(source_file_path=LOGS_FILE_NAME, target_file_path=LOGS_FILE_NAME)


def pipeline():
    try:
        # extract data
        response = get_faker_data(quantity=FAKER_QUANTITY)

        # log failure
        if not response:
            raise Exception("Failed to get response from API.")

        data, errors = validate_response(response=response)

        if not data:
            save_failed_response(
                response=response,
                errors=errors,
            )
            raise Exception("Response failed validation.")

        load_success = load_data_to_gcs(data=data)

        if not load_success:
            raise Exception("Failed to upload to GCS.")

        validation_success = validate_presence_of_file(target_file_path=BLOB_NAME)

        if not validation_success:
            raise Exception("Blob not present in GCS bucket.")
    except Exception as e:
        logger.error(e)

    finally:
        save_logs()


if __name__ == "__main__":
    pipeline()

    list_gcs_objects("james_walden")
