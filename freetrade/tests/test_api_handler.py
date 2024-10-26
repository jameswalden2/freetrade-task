from unittest.mock import Mock

import pytest
from requests.exceptions import HTTPError, Timeout

from freetrade.api_handler import get_request

# Define RETRIES and BACKOFF_FACTOR for testing purposes
RETRIES = 3
BACKOFF_FACTOR = 0.1


def test_successful_request(mocker):
    mock_response = Mock()
    mock_response.json.return_value = {"key": "value"}
    mock_response.raise_for_status = Mock()
    mocker.patch("requests.get", return_value=mock_response)

    result = get_request("http://example.com")
    assert result == {"key": "value"}


def test_http_error(mocker, caplog):
    mocker.patch(
        "requests.get", side_effect=HTTPError("404 Client Error: Not Found for url")
    )

    with caplog.at_level("ERROR"):
        result = get_request("http://example.com")
        assert result is None
        assert "HTTP error: 404 Client Error" in caplog.text


def test_transient_error_then_success(mocker, caplog):
    # Mock two timeouts followed by a successful response
    mock_response = Mock()
    mock_response.json.return_value = {"key": "value"}
    mocker.patch(
        "requests.get",
        side_effect=[
            Timeout("Connection timed out"),
            mock_response,
        ],
    )
    mocker.patch("time.sleep", return_value=None)

    with caplog.at_level("INFO"):
        result = get_request("http://example.com")
        assert result == {"key": "value"}
        assert "Retrying in" in caplog.text


def test_all_retries_fail(mocker, caplog):
    mocker.patch("requests.get", side_effect=Timeout("Connection timed out"))
    mocker.patch("time.sleep", return_value=None)

    with caplog.at_level("ERROR"):
        result = get_request("http://example.com")
        assert result is None
        assert "All retry attempts failed." in caplog.text
