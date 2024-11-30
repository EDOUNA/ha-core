from collections.abc import Generator
import logging
from unittest.mock import AsyncMock, patch

import orjson
import pytest
from tadoasync.models import (
    Capabilities,
    Device,
    GetMe,
    HomeState,
    MobileDevice,
    Weather,
    Zone,
    ZoneState,
)

from tests.common import MockConfigEntry, load_fixture

_LOGGER = logging.getLogger(__name__)


ZONE_FIXTURES = {
    6: {
        "state": "tado/smartac4.with_fanlevel.json",
        "capabilities": "tado/zone_with_fanlevel_horizontal_vertical_swing.json",
    },
    5: {
        "state": "tado/smartac3.with_swing.json",
        "capabilities": "tado/zone_with_swing_capabilities.json",
    },
    4: {
        "state": "tado/tadov2.water_heater.heating.json",
        "capabilities": "tado/water_heater_zone_capabilities.json",
    },
    3: {
        "state": "tado/smartac3.cool_mode.json",
        "capabilities": "tado/zone_capabilities.json",
    },
    2: {
        "state": "tado/tadov2.water_heater.auto_mode.json",
        "capabilities": "tado/water_heater_zone_capabilities.json",
    },
    1: {
        "state": "tado/tadov2.heating.manual_mode.json",
        "capabilities": "tado/tadov2.zone_capabilities.json",
    },
}


def get_zone_fixture(zone_id: int, fixture_type: str) -> AsyncMock:
    """Return mocked zone fixture (state or capabilities) based on the zone ID and type."""
    _LOGGER.debug("Erwin: get_zone_fixture(%s, %s)", zone_id, fixture_type)
    if zone_id not in ZONE_FIXTURES:
        raise ValueError(f"Unknown zone ID: {zone_id}")
    if fixture_type not in ZONE_FIXTURES[zone_id]:
        raise ValueError(f"Unknown fixture type: {fixture_type}")

    if fixture_type == "state":
        return AsyncMock(
            return_value=ZoneState.from_json(
                load_fixture(ZONE_FIXTURES[zone_id][fixture_type])
            )
        )

    return AsyncMock(
        return_value=Capabilities.from_json(
            load_fixture(ZONE_FIXTURES[zone_id][fixture_type])
        )
    )


@pytest.fixture(name="mock_tado_client")
def mock_tado_client() -> Generator[AsyncMock, None, None]:
    """Mock the Tado client."""
    with patch(
        "homeassistant.components.tado.tado_connector.Tado", autospec=True
    ) as mock_tado_class:
        mock_tado = mock_tado_class.return_value

        mock_tado.get_me.return_value = GetMe.from_json(load_fixture("tado/me.json"))
        mock_tado.get_weather.return_value = Weather.from_json(
            load_fixture("tado/weather.json")
        )
        mock_tado.get_home_state.return_value = HomeState.from_json(
            load_fixture("tado/home_state.json")
        )

        # Load the devices from the fixture
        mock_tado.get_devices.return_value = [
            Device.from_dict(device)
            for device in orjson.loads(load_fixture("tado/devices.json"))
        ]

        # Load the mobile devices, in the same way
        mock_tado.get_mobile_devices.return_value = [
            MobileDevice.from_dict(mobile_device)
            for mobile_device in orjson.loads(load_fixture("tado/mobile_devices.json"))
        ]

        # TODO: seems like this isn't properly loaded
        mock_tado.get_zones.return_value = [
            Zone.from_dict(zone)
            for zone in orjson.loads(load_fixture("tado/zones.json"))
        ]

        mock_tado.get_zone_state.side_effect = lambda zone_id: get_zone_fixture(
            zone_id, "state"
        )
        mock_tado.get_capabilities.side_effect = lambda zone_id: get_zone_fixture(
            zone_id, "capabilities"
        )
        # TODO: fix this later
        # mock_tado.get_device_info.return_value = Device.from_json(
        #     load_fixture("tado/device_temp_offset.json")
        # )

        yield mock_tado


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Mock a config entry for the Tado integration."""
    return MockConfigEntry(
        domain="tado",
        data={"username": "mock_user", "password": "mock_password"},
        options={"fallback": "NEXT_TIME_BLOCK"},
    )


@pytest.fixture(name="setup_tado_integration")
async def setup_tado_integration(hass, mock_tado_client, mock_config_entry):
    """Fixture to set up the Tado integration."""
    _LOGGER.debug("Erwin: setup_tado_integration")
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
