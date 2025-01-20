"""Test the sma init file."""

from datetime import timedelta
import logging
from unittest.mock import patch

from freezegun.api import FrozenDateTimeFactory
from pysma.exceptions import (
    SmaAuthenticationException,
    SmaConnectionException,
    SmaReadException,
)
import pytest

from homeassistant.components.sma import DEFAULT_SCAN_INTERVAL
from homeassistant.components.sma.const import DOMAIN
from homeassistant.config_entries import SOURCE_IMPORT, SOURCE_USER, ConfigEntryState
from homeassistant.core import HomeAssistant

from . import MOCK_DEVICE, MOCK_USER_INPUT, _patch_async_setup_entry

from tests.common import MockConfigEntry, async_fire_time_changed

_LOGGER = logging.getLogger(__name__)


async def test_migrate_entry_minor_version_1_2(hass: HomeAssistant) -> None:
    """Test migrating a 1.1 config entry to 1.2."""
    with _patch_async_setup_entry():
        entry = MockConfigEntry(
            domain=DOMAIN,
            title=MOCK_DEVICE["name"],
            unique_id=MOCK_DEVICE["serial"],  # Not converted to str
            data=MOCK_USER_INPUT,
            source=SOURCE_IMPORT,
            minor_version=1,
        )
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        assert entry.version == 1
        assert entry.minor_version == 2
        assert entry.unique_id == str(MOCK_DEVICE["serial"])


@pytest.mark.parametrize(
    "exception",
    [
        SmaAuthenticationException,
        SmaConnectionException,
        SmaReadException,
    ],
)
async def test_setup_exceptions(hass: HomeAssistant, exception: Exception) -> None:
    """Test the setup exceptions."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=MOCK_DEVICE["name"],
        unique_id=MOCK_DEVICE["serial"],
        data=MOCK_USER_INPUT,
        source=SOURCE_USER,
        minor_version=1,
    )
    entry.add_to_hass(hass)

    with patch("pysma.SMA.new_session", side_effect=exception):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # In case of SmaAuthenticationException it's SETUP_ERROR, other errors result in SETUP_RETRY
    expected_state = (
        ConfigEntryState.SETUP_ERROR
        if exception is SmaAuthenticationException
        else ConfigEntryState.SETUP_RETRY
    )
    assert entry.state is expected_state


@pytest.mark.parametrize(
    "exception",
    [
        SmaConnectionException,
        SmaReadException,
    ],
)
async def test_async_update_data_exceptions(
    hass: HomeAssistant,
    exception: Exception,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test the async_update_data exceptions."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=MOCK_DEVICE["name"],
        unique_id=MOCK_DEVICE["serial"],
        data=MOCK_USER_INPUT,
        source=SOURCE_USER,
        minor_version=1,
    )
    entry.add_to_hass(hass)

    with (
        patch(
            "homeassistant.components.sma.__init__.pysma.SMA.new_session",
            return_value=True,
        ),
        patch(
            "homeassistant.components.sma.__init__.pysma.SMA.device_info",
            return_value=MOCK_DEVICE,
        ),
        _patch_async_setup_entry() as mock_setup_entry,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert len(mock_setup_entry.mock_calls) == 1
    assert entry.version == 1
    assert entry.minor_version == 2
    assert entry.unique_id == str(MOCK_DEVICE["serial"])

    assert entry.state is ConfigEntryState.LOADED

    coordinator = hass.data["sma"][entry.entry_id]
    _LOGGER.debug("Coordinator: %s", coordinator)

    with patch(
        "homeassistant.components.sma.__init__.pysma.SMA.read", return_value=True
    ):
        freezer.tick(timedelta(seconds=DEFAULT_SCAN_INTERVAL))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()

        assert coordinator.data is not None
        assert coordinator.data["serial"] == MOCK_DEVICE["serial"]
        assert coordinator.data["name"] == MOCK_DEVICE["name"]
