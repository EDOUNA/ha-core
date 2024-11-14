"""Test the Tado config flow."""

from ipaddress import ip_address
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import tadoasync
import tadoasync.models

from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.components.tado.config_flow import NoHomes
from homeassistant.components.tado.const import (
    CONF_FALLBACK,
    CONST_OVERLAY_TADO_DEFAULT,
    DOMAIN,
)
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.common import MockConfigEntry

_LOGGER = logging.getLogger(__name__)


import tadoasync


def _get_mock_tado_api(get_me=None) -> MagicMock:
    mock_tado = MagicMock(spec=tadoasync.Tado)

    if isinstance(get_me, Exception):
        mock_tado.get_me = AsyncMock(side_effect=get_me)
    else:
        mock_tado.get_me = AsyncMock(
            return_value=get_me
            or tadoasync.models.GetMe(
                name="Tado Enthusiast",
                email="email@mail.com",
                id="random_id-198a8aa-8a8a-8a8a-8a8a-8a8a8a8a8a8a",
                username="email@mail.com",
                locale="nl",
                homes=[tadoasync.models.Home(id=1, name="myhome")],
            )
        )

    mock_tado.login = AsyncMock(return_value=None)
    mock_tado.close = AsyncMock(return_value=None)
    return mock_tado


@pytest.mark.parametrize(
    ("exception", "error"),
    [
        (KeyError, "invalid_auth"),
        (RuntimeError, "cannot_connect"),
        (ValueError, "unknown"),
    ],
)
async def test_form_exceptions(
    hass: HomeAssistant, exception: Exception, error: str
) -> None:
    """Test we handle Form Exceptions."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    mock_tado_api = MagicMock(spec=tadoasync.Tado)
    mock_tado_api.get_me = AsyncMock(side_effect=exception)
    mock_tado_api.login = AsyncMock(return_value=None)
    mock_tado_api.close = AsyncMock(return_value=None)

    with patch(
        "homeassistant.components.tado.config_flow.Tado",
        return_value=mock_tado_api,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"username": "test-username", "password": "test-password"},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": error}

    # Test a retry to recover, upon failure
    mock_tado_api = MagicMock(spec=tadoasync.Tado)
    mock_tado_api.get_me = AsyncMock(
        return_value=tadoasync.models.GetMe(
            name="Tado Enthusiast",
            email="email@mail.com",
            id="random_id-198a8aa-8a8a-8a8a-8a8a-8a8a8a8a8a8a",
            username="email@mail.com",
            locale="nl",
            homes=[tadoasync.models.Home(id=1, name="myhome")],
        )
    )
    mock_tado_api.login = AsyncMock(return_value=None)
    mock_tado_api.close = AsyncMock(return_value=None)

    with (
        patch(
            "homeassistant.components.tado.config_flow.Tado",
            return_value=mock_tado_api,
        ),
        patch(
            "homeassistant.components.tado.async_setup_entry",
            return_value=True,
        ) as mock_setup_entry,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"username": "test-username", "password": "test-password"},
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "myhome"
    assert result["data"] == {
        "username": "test-username",
        "password": "test-password",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_options_flow(hass: HomeAssistant) -> None:
    """Test config flow options."""
    entry = MockConfigEntry(domain=DOMAIN, data={"username": "test-username"})
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "homeassistant.components.tado.async_setup_entry",
        return_value=True,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(
        entry.entry_id, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CONF_FALLBACK: CONST_OVERLAY_TADO_DEFAULT},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_FALLBACK: CONST_OVERLAY_TADO_DEFAULT}


async def test_create_entry(hass: HomeAssistant) -> None:
    """Test we can setup though the user path."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    mock_tado_api = _get_mock_tado_api()
    _LOGGER.debug("Mock Tado API: %s", mock_tado_api)
    with (
        patch(
            "homeassistant.components.tado.config_flow.Tado",
            return_value=mock_tado_api,
        ),
        patch(
            "homeassistant.components.tado.async_setup_entry",
            return_value=True,
        ) as mock_setup_entry,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"username": "test-username", "password": "test-password"},
        )
        await hass.async_block_till_done()

    _LOGGER.debug("Result after async_configure: %s", result)
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "myhome"
    assert result["data"] == {
        "username": "test-username",
        "password": "test-password",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_auth(hass: HomeAssistant) -> None:
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    mock_tado_api = _get_mock_tado_api(
        get_me=tadoasync.exceptions.TadoAuthenticationError()
    )

    with patch(
        "homeassistant.components.tado.config_flow.Tado",
        return_value=mock_tado_api,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"username": "test-username", "password": "test-password"},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    mock_tado_api = _get_mock_tado_api(
        get_me=tadoasync.exceptions.TadoConnectionError()
    )

    with patch(
        "homeassistant.components.tado.config_flow.Tado",
        return_value=mock_tado_api,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"username": "test-username", "password": "test-password"},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_no_homes(hass: HomeAssistant) -> None:
    """Test we handle no homes error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    mock_tado_api = _get_mock_tado_api(
        get_me=tadoasync.models.GetMe(
            name="Tado Enthusiast",
            email="email@mail.com",
            id="random_id-198a8aa-8a8a-8a8a-8a8a-8a8a8a8a8a8a",
            username="email@mail.com",
            locale="nl",
            homes=[],
        )
    )

    with patch(
        "homeassistant.components.tado.config_flow.Tado",
        return_value=mock_tado_api,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"username": "test-username", "password": "test-password"},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "no_homes"}


async def test_form_homekit(hass: HomeAssistant) -> None:
    """Test that we abort from homekit if tado is already setup."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_HOMEKIT},
        data=zeroconf.ZeroconfServiceInfo(
            ip_address=ip_address("127.0.0.1"),
            ip_addresses=[ip_address("127.0.0.1")],
            hostname="mock_hostname",
            name="mock_name",
            port=None,
            properties={zeroconf.ATTR_PROPERTIES_ID: "AA:BB:CC:DD:EE:FF"},
            type="mock_type",
        ),
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}
    flow = next(
        flow
        for flow in hass.config_entries.flow.async_progress()
        if flow["flow_id"] == result["flow_id"]
    )
    assert flow["context"]["unique_id"] == "AA:BB:CC:DD:EE:FF"

    entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_USERNAME: "mock", CONF_PASSWORD: "mock"}
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_HOMEKIT},
        data=zeroconf.ZeroconfServiceInfo(
            ip_address=ip_address("127.0.0.1"),
            ip_addresses=[ip_address("127.0.0.1")],
            hostname="mock_hostname",
            name="mock_name",
            port=None,
            properties={zeroconf.ATTR_PROPERTIES_ID: "AA:BB:CC:DD:EE:FF"},
            type="mock_type",
        ),
    )
    assert result["type"] is FlowResultType.ABORT


@pytest.mark.parametrize(
    ("exception", "error"),
    [
        (tadoasync.exceptions.TadoAuthenticationError, "invalid_auth"),
        (RuntimeError, "cannot_connect"),
        (NoHomes, "no_homes"),
        (ValueError, "unknown"),
    ],
)
async def test_reconfigure_flow(
    hass: HomeAssistant, exception: Exception, error: str
) -> None:
    """Test re-configuration flow."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "username": "test-username",
            "password": "test-password",
            "home_id": 1,
        },
        unique_id="unique_id",
    )
    entry.add_to_hass(hass)

    mock_tado_api = MagicMock(spec=tadoasync.Tado)
    mock_tado_api.get_me = AsyncMock(side_effect=exception)
    mock_tado_api.login = AsyncMock(return_value=None)
    mock_tado_api.close = AsyncMock(return_value=None)

    result = await entry.start_reconfigure_flow(hass)

    assert result["type"] is FlowResultType.FORM

    with patch(
        "homeassistant.components.tado.config_flow.Tado",
        return_value=mock_tado_api,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_PASSWORD: "test-password",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.FORM
    _LOGGER.debug("Result after async_configure: %s", result)
    assert result["errors"] == {"base": error}

    mock_tado_api = MagicMock(spec=tadoasync.Tado)
    mock_tado_api.get_me = AsyncMock(
        return_value=tadoasync.models.GetMe(
            name="Tado Enthusiast",
            email="email@mail.com",
            id="random_id-198a8aa-8a8a-8a8a-8a8a-8a8a8a8a8a8a",
            username="email@mail.com",
            locale="nl",
            homes=[tadoasync.models.Home(id=1, name="myhome")],
        )
    )
    mock_tado_api.login = AsyncMock(return_value=None)
    mock_tado_api.close = AsyncMock(return_value=None)

    with (
        patch(
            "homeassistant.components.tado.config_flow.Tado",
            return_value=mock_tado_api,
        ),
        patch(
            "homeassistant.components.tado.async_setup_entry",
            return_value=True,
        ),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_PASSWORD: "test-password",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    entry = hass.config_entries.async_get_entry(entry.entry_id)
    assert entry
    assert entry.title == "Mock Title"
    assert entry.data == {
        "username": "test-username",
        "password": "test-password",
        "home_id": 1,
    }
