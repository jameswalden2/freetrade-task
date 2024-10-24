import json
import os
import sys
import tempfile

import pandas as pd
import requests
from google.cloud import storage
from pydantic import ValidationError
from requests import HTTPError

from freetrade.models import FakerData, FakerResponse


def get_faker_data(quantity: int | None = None) -> dict | None:
    FAKER_URL = "https://fakerapi.it/api/v1/users?_quantity=100"
    FAKER_QUANTITY_DEFAULT = 1

    # if quantity is None:
    #     quantity = FAKER_QUANTITY_DEFAULT

    # FAKER_URL = FAKER_URL.format(quantity=quantity)

    try:
        response = requests.get(FAKER_URL).json()
        return response
    except HTTPError as e:
        print(e.json())


def validate_response(response: dict) -> list[FakerData]:
    try:
        response: FakerResponse = FakerResponse(**response)
        return response.data
    except ValidationError as e:
        print(e.json())


def load_data_to_gcs(data: list[FakerData]):

    data_as_json = [x.model_dump() for x in data]

    print(data_as_json[0:2])

    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".json", mode="w"
    ) as temp_file:
        json.dump(data_as_json, temp_file)
        temp_file_path = temp_file.name

    storage_client = storage.Client.create_anonymous_client()
    bucket = storage_client.bucket("freetrade-data-eng-hiring")
    blob = bucket.blob("james_walden/dev/data_engineering_task.json")
    blob.upload_from_filename(temp_file_path)

    print(temp_file_path)

    os.remove(temp_file_path)


def list_gcs_objects():
    storage_client = storage.Client.create_anonymous_client()
    blobs = storage_client.list_blobs(
        "freetrade-data-eng-hiring", prefix="james_walden"
    )

    for blob in blobs:
        print(blob.name)


if __name__ == "__main__":
    # response = get_faker_data(quantity=100)
    # data = validate_response(response=response)

    # load_data_to_gcs(data=data)

    list_gcs_objects()
