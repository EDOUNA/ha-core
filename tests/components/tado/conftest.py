"""Asynchronous Python client for Tado."""

from collections.abc import AsyncGenerator, Generator

import aiohttp
from aioresponses import aioresponses
import pytest
from tadoasync import Tado

from .const import TADO_TOKEN_URL

from tests.common import load_fixture


@pytest.fixture(name="python_tado")
async def client() -> AsyncGenerator[Tado, None]:
    """Return a Tado client."""
    async with (
        aiohttp.ClientSession() as session,
        Tado(
            username="username",
            password="password",
            session=session,
            request_timeout=10,
        ) as tado,
    ):
        yield tado


@pytest.fixture(autouse=True)
def _tado_oauth(responses: aioresponses) -> None:
    """Mock the Tado token URL."""
    print("Mocking Tado token URL and /me endpoint")
    responses.post(
        TADO_TOKEN_URL,
        status=200,
        payload={
            "access_token": "test_access_token",
            "expires_in": 3600,
            "refresh_token": "test_refresh_token",
        },
    )
    responses.get(
        "https://my.tado.com/api/v2/me",
        status=200,
        body=load_fixture("tado/me.json"),
    )


@pytest.fixture(name="responses")
def aioresponses_fixture() -> Generator[aioresponses, None, None]:
    """Return aioresponses fixture."""
    with aioresponses() as mocked_responses:
        yield mocked_responses
