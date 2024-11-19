from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest

from tests.common import MockConfigEntry, load_fixture


@pytest.fixture
def mock_tado_client() -> Generator[AsyncMock]:
    """Mock the Tado client."""
    with patch(
        "homeassistant.components.tado.tado_connector.Tado", autospec=True
    ) as mock_tado_class:
        # Mock the Tado instance
        mock_tado = mock_tado_class.return_value

        # Define all fixtures for mocked methods
        mock_tado.get_me.return_value = AsyncMock(
            return_value=load_fixture("tado/me.json")
        )
        mock_tado.get_weather.return_value = AsyncMock(
            return_value=load_fixture("tado/weather.json")
        )
        mock_tado.get_devices.return_value = AsyncMock(
            return_value=load_fixture("tado/devices.json")
        )
        mock_tado.get_mobile_devices.return_value = AsyncMock(
            return_value=load_fixture("tado/mobile_devices.json")
        )
        mock_tado.get_zones.return_value = AsyncMock(
            return_value=load_fixture("tado/zones.json")
        )
        mock_tado.get_home_state.return_value = AsyncMock(
            return_value=load_fixture("tado/home_state.json")
        )
        mock_tado.get_zone_state.side_effect = lambda zone_id: AsyncMock(
            return_value=load_fixture(f"tado/zone_{zone_id}_state.json")
        )
        mock_tado.get_capabilities.side_effect = lambda zone_id: AsyncMock(
            return_value=load_fixture(f"tado/zone_{zone_id}_capabilities.json")
        )
        # mock_tado.get_default_overlay.side_effect = lambda zone_id: AsyncMock(
        #    return_value=load_fixture("tado/zone_default_overlay.json")
        # )
        mock_tado.get_device_info.side_effect = AsyncMock(
            return_value=load_fixture("tado/device_temp_offset.json")
        )

        yield mock_tado


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Mock a config entry for the Tado integration."""
    return MockConfigEntry(
        domain="tado",
        data={"username": "mock_user", "password": "mock_password"},
        options={"fallback": "NEXT_TIME_BLOCK"},
    )


@pytest.fixture
async def setup_tado_integration(hass, mock_tado_client, mock_config_entry):
    """Fixture to set up the Tado integration."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
