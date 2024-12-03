from collections.abc import Generator
import logging
from unittest.mock import AsyncMock, patch

import orjson
import pytest
from tadoasync import Tado
from tadoasync.models import (
    Capabilities,
    Device,
    GetMe,
    HomeState,
    MobileDevice,
    TemperatureOffset,
    Weather,
    Zone,
    ZoneState,
    ZoneStates,
)

from homeassistant.core import HomeAssistant

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


def get_zone_fixture(zone_id: int, fixture_type: str) -> ZoneState | Capabilities:
    """Return mocked zone fixture (state or capabilities) based on the zone ID and type."""
    if zone_id not in ZONE_FIXTURES:
        raise ValueError(f"Unknown zone ID: {zone_id}")
    if fixture_type not in ZONE_FIXTURES[zone_id]:
        raise ValueError(f"Unknown fixture type: {fixture_type}")

    if fixture_type == "state":
        return ZoneState.from_json(load_fixture(ZONE_FIXTURES[zone_id][fixture_type]))
    return Capabilities.from_json(load_fixture(ZONE_FIXTURES[zone_id][fixture_type]))


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

        mock_tado.get_devices.return_value = [
            Device.from_dict(device)
            for device in orjson.loads(load_fixture("tado/devices.json"))
        ]
        mock_tado.get_mobile_devices.return_value = [
            MobileDevice.from_dict(mobile_device)
            for mobile_device in orjson.loads(load_fixture("tado/mobile_devices.json"))
        ]
        mock_tado.get_zones.return_value = [
            Zone.from_dict(zone)
            for zone in orjson.loads(load_fixture("tado/zones.json"))
        ]

        # TODO: OLD VERSION
        # zone_states_json = orjson.loads(load_fixture("tado/zone_states.json"))
        # zone_states = {
        #     zone_id: ZoneState.from_dict(zone_state_dict)
        #     for zone_id, zone_state_dict in zone_states_json["zoneStates"].items()
        # }

        # mock_tado.get_zone_states.return_value = [ZoneStates(zone_states=zone_states)]

        # Mock the get_zone_states method
        async def mock_get_zone_states():
            zone_states_json = orjson.loads(load_fixture("tado/zone_states.json"))
            zone_states = {
                zone_id: ZoneState.from_dict(zone_state_dict)
                for zone_id, zone_state_dict in zone_states_json["zoneStates"].items()
            }

            for zone_state in zone_states.values():
                await Tado.update_zone_data(mock_tado, zone_state)

            updated_zone_states = ZoneStates(zone_states=zone_states)
            return [updated_zone_states]

        mock_tado.get_zone_states.side_effect = mock_get_zone_states

        async def mock_get_zone_state(zone_id: int):
            zone_state_json = load_fixture(ZONE_FIXTURES[zone_id]["state"])
            zone_state = ZoneState.from_json(zone_state_json)
            await Tado.update_zone_data(mock_tado, zone_state)
            return zone_state

        mock_tado.get_zone_state.side_effect = mock_get_zone_state
        # mock_tado.get_zone_state.side_effect = lambda zone_id: get_zone_fixture(
        #     zone_id, "state"
        # )

        mock_tado.get_capabilities.side_effect = lambda zone_id: get_zone_fixture(
            zone_id, "capabilities"
        )

        # TODO: put in the default overlay

        # TODO: put in the WR1 device
        # m.get(
        #     "https://my.tado.com/api/v2/devices/WR1/",
        #     payload=load_fixture(device_wr1_fixture),
        # )

        # Mock the async get_device_info method
        async def mock_get_device_info(
            serial_no: str, attribute: str | None = None
        ) -> Device | TemperatureOffset:
            if attribute == "temperatureOffset":
                response = load_fixture("tado/device_temp_offset.json")
                return TemperatureOffset.from_json(response)
            response = load_fixture("tado/device_wr1.json")
            return Device.from_json(response)

        mock_tado.get_device_info.side_effect = mock_get_device_info

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
async def setup_tado_integration(
    hass: HomeAssistant, mock_tado_client, mock_config_entry
):
    """Fixture to set up the Tado integration."""
    _LOGGER.debug("Erwin: setup_tado_integration")
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
