import json

import pytest

from freetrade.models import FakerData, FakerResponse


@pytest.fixture
def example_data():
    data = {
        "id": 1,
        "uuid": "8ddd6660-3543-3cfc-bc7c-4fa0bff3b448",
        "firstname": "Murphy",
        "lastname": "Walter",
        "username": "mckenzie97",
        "password": 'jQb-);RX"',
        "email": "jacobson.anderson@effertz.org",
        "ip": "156.168.202.126",
        "macAddress": "10:51:9d:a9:51:5e",
        "website": "http://schulist.org/",
        "image": "http://placeimg.com/640/480/people",
        "pipeline_id": "t76zVypY3Y",
        "pipeline_timestamp": "2024-10-26T13:04:35.033643",
    }
    return data


@pytest.fixture
def example_response(example_data):
    return {"field": "stuff", "data": [example_data]}


def test_validate_faker_data(example_data):
    faker_data = FakerData(**example_data)

    assert faker_data.id == example_data["id"]


def test_validate_faker_response(example_data, example_response):

    response = FakerResponse(**example_response)

    assert len(response.data) == 1
    assert response.data[0] == FakerData(**example_data)
