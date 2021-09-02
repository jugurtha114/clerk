import pytest
import responses
import requests
from unittest import mock

from microsoft.base import BaseEndpoint
from microsoft.helpers import BASE_URL

from django.conf import settings

TEST_URL = "https://github.com/getsentry/responses"


@pytest.fixture
def mock_client():
    """DRY: mock the client when BaseEndpoint object is created."""
    with mock.patch("microsoft.base.create_client") as mock_create_client:
        mock_client = mock.Mock()
        mock_client.acquire_token_silent.return_value = {"access_token": "1805"}
        mock_create_client.return_value = mock_client
        yield mock_client


def test_constructor(mock_client):
    base = BaseEndpoint()

    mock_client.acquire_token_silent.assert_called_once()
    assert base.headers["Authorization"] == "Bearer 1805"


@responses.activate
def test_handle_success_body(mock_client):
    responses.add(
        responses.GET,
        TEST_URL,
        json={"message": "test request success"},
        status=200,
    )

    base = BaseEndpoint()
    resp = requests.get(TEST_URL)
    result = base.handle(resp)

    assert result["message"] == "test request success"


@responses.activate
def test_handle_success_nobody(mock_client):
    responses.add(
        responses.GET,
        TEST_URL,
        status=200,
    )

    base = BaseEndpoint()
    resp = requests.get(TEST_URL)
    result = base.handle(resp)

    assert result == None


@responses.activate
def test_handle_fail_body(mock_client):
    responses.add(
        responses.GET,
        TEST_URL,
        json={"message": "test request fail"},
        status=404,
    )

    with pytest.raises(requests.HTTPError):
        base = BaseEndpoint()
        resp = requests.get(TEST_URL)
        base.handle(resp)


@responses.activate
def test_handle_fail_nobody(mock_client):
    responses.add(
        responses.GET,
        TEST_URL,
        status=404,
    )

    with pytest.raises(requests.HTTPError):
        base = BaseEndpoint()
        resp = requests.get(TEST_URL)
        base.handle(resp)


@responses.activate
def test_get_success(mock_client):
    userPrincipalName = "bugs.bunny@anikalegal.com"
    responses.add(
        responses.GET,
        BASE_URL + "users/" + userPrincipalName,
        json={"userPrincipalName": userPrincipalName},
        status=200,
    )

    base = BaseEndpoint()
    result = base.get("users/" + userPrincipalName)

    assert result["userPrincipalName"] == userPrincipalName


@responses.activate
def test_get_fail(mock_client):
    userPrincipalName = "buy.bunny@anikalegal.com"
    responses.add(
        responses.GET,
        BASE_URL + "users/" + userPrincipalName,
        json={"error": {"code": "Request_ResourceNotFound"}},
        status=404,
    )

    with pytest.raises(requests.HTTPError):
        base = BaseEndpoint()
        base.get("users/" + userPrincipalName)