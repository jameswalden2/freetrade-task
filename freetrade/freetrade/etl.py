import json
import os
import tempfile

from pydantic import ValidationError

from freetrade import (
    BLOB_NAME,
    FAKER_QUANTITY,
    RUN_IDENTIFIER,
    RUN_TIMESTAMP,
    RUN_TIMESTAMP_STR,
    RUN_UNIQUE_ID,
)
from freetrade.api_handler import get_request
from freetrade.gcs import get_gcs_object, upload_to_gcs
from freetrade.logger import LOGS_FILE_NAME, logger
from freetrade.models import FakerData, FakerResponse


def get_faker_data(quantity: int) -> dict | None:
    """Makes a get request for new faker data.

    Args:
        quantity (int): the quantity of users to retrieve.

    Returns:
        dict | None: a dictionary response or None if the request fails.
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
            logger.info(error)

    return None, error_strs


def transform_data(data: list[FakerData]) -> list[FakerData]:
    """Transform data by adding pipeline id and pipeline timestamp.

    Args:
        data (list[FakerData]): list of data to transform.

    Returns:
        list[FakerData]: list of transformed data.
    """
    for x in data:
        # add run id
        x.pipeline_id = RUN_UNIQUE_ID
        # add run timestamp
        x.pipeline_timestamp = RUN_TIMESTAMP

    return data


def load_data_to_gcs(data: list[FakerData]) -> bool:
    """Upload data to gcs, both to target and history.

    Args:
        data (list[FakerData]): list of data to upload.

    Returns:
        bool: success status of upload.
    """
    data_as_json = [x.model_dump_json(serialize_as_any=True) for x in data]

    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".json", mode="w"
        ) as temp_file:
            for data in data_as_json:
                temp_file.write(data)
                temp_file.write("\n")

            temp_file_name = temp_file.name

        # upload to main target
        upload_to_gcs(
            source_file_path=temp_file_name,
            target_file_path=BLOB_NAME,
        )
        # upload to history
        upload_to_gcs(
            source_file_path=temp_file_name,
            target_file_path=f"history/{RUN_IDENTIFIER}.json",
        )

        os.remove(temp_file_name)
        return True
    except Exception as e:
        logger.error(e)
        return False


def check_uploaded_file(expected_data: list[FakerData]) -> bool:
    """Check uploaded file.

    Args:
        data (list[FakerData]): list of data to validate has been uploaded.

    Returns:
        bool: success status of upload.
    """
    uploaded_data = get_gcs_object(target_file_path=BLOB_NAME)

    return len(uploaded_data) == len(expected_data)


def save_failed_response(response: dict, errors: list[str]):
    """Save response that failed validation.

    Args:
        response (dict): response that failed validation.
        errors (list[str]): list of errors.
    """
    failed_response = {"errors": errors, "response": response}

    target_file_path = f"failed/{RUN_IDENTIFIER}_response.json"

    with tempfile.NamedTemporaryFile(suffix=".json", mode="w") as temp_file:
        json.dump(failed_response, temp_file)
        upload_to_gcs(
            source_file_path=temp_file.name,
            target_file_path=target_file_path,
        )


def save_logs():
    """Save logs to gcs."""
    upload_to_gcs(source_file_path=LOGS_FILE_NAME, target_file_path=LOGS_FILE_NAME)


def pipeline():
    """Pipeline function."""
    logger.info(f"Starting run with ID: {RUN_UNIQUE_ID} at {RUN_TIMESTAMP_STR}.")
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

        transformed_data = transform_data(data=data)

        load_success = load_data_to_gcs(data=transformed_data)

        if not load_success:
            raise Exception("Failed to upload to GCS.")

        validation_success = check_uploaded_file(expected_data=transformed_data)

        if not validation_success:
            raise Exception("Blob not uploaded correctly in GCS bucket.")
    except Exception as e:
        logger.error(e)
        logger.error("PIPELINE FAILED")
        raise Exception("Pipeline failed, see traceback.")

    finally:
        logger.info("Pipeline successful.")
        save_logs()


if __name__ == "__main__":
    pipeline()
