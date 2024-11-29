"""Asynchronous Python client for Tado."""

import logging
from unittest.mock import patch

from aioresponses import aioresponses
import pytest

from homeassistant.components.tado import DOMAIN
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry, load_json_value_fixture

_LOGGER = logging.getLogger(__name__)


@pytest.fixture
async def init_tado_integration_with_mock(hass: HomeAssistant):
    """Initialize the Tado integration with a mocked client."""
    with patch(
        "homeassistant.components.tado.tado_connector.Tado", autospec=True
    ) as mock_tado_class:
        mock_tado = mock_tado_class.return_value
        mock_tado.login.return_value = None
        await async_init_tado_integration(hass)


async def async_init_tado_integration(
    hass: HomeAssistant,
    skip_setup: bool = False,
):
    """Set up the tado integration in Home Assistant."""

    token_fixture = "tado/token.json"
    devices_fixture = "tado/devices.json"
    mobile_devices_fixture = "tado/mobile_devices.json"
    me_fixture = "tado/me.json"
    weather_fixture = "tado/weather.json"
    home_state_fixture = "tado/home_state.json"
    zones_fixture = "tado/zones.json"
    zone_states_fixture = "tado/zone_states.json"

    # WR1 Device
    device_wr1_fixture = "tado/device_wr1.json"

    # Smart AC with fanLevel, Vertical and Horizontal swings
    zone_6_state_fixture = "tado/smartac4.with_fanlevel.json"
    zone_6_capabilities_fixture = (
        "tado/zone_with_fanlevel_horizontal_vertical_swing.json"
    )

    # Smart AC with Swing
    zone_5_state_fixture = "tado/smartac3.with_swing.json"
    zone_5_capabilities_fixture = "tado/zone_with_swing_capabilities.json"

    # Water Heater 2
    zone_4_state_fixture = "tado/tadov2.water_heater.heating.json"
    zone_4_capabilities_fixture = "tado/water_heater_zone_capabilities.json"

    # Smart AC
    zone_3_state_fixture = "tado/smartac3.cool_mode.json"
    zone_3_capabilities_fixture = "tado/zone_capabilities.json"

    # Water Heater
    zone_2_state_fixture = "tado/tadov2.water_heater.auto_mode.json"
    zone_2_capabilities_fixture = "tado/water_heater_zone_capabilities.json"

    # Tado V2 with manual heating
    zone_1_state_fixture = "tado/tadov2.heating.manual_mode.json"
    zone_1_capabilities_fixture = "tado/tadov2.zone_capabilities.json"

    # Device Temp Offset
    device_temp_offset = "tado/device_temp_offset.json"

    # Zone Default Overlay
    zone_def_overlay = "tado/zone_default_overlay.json"

    with aioresponses() as m:
        m.post(
            "https://auth.tado.com/oauth/token",
            payload=load_json_value_fixture(token_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/me", payload=load_json_value_fixture(me_fixture)
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/weather",
            payload=load_json_value_fixture(weather_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/state",
            payload=load_json_value_fixture(home_state_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/devices",
            payload=load_json_value_fixture(devices_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/mobileDevices",
            payload=load_json_value_fixture(mobile_devices_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/devices/WR1/",
            payload=load_json_value_fixture(device_wr1_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/devices/WR1/temperatureOffset",
            payload=load_json_value_fixture(device_temp_offset),
        )
        m.get(
            "https://my.tado.com/api/v2/devices/WR4/temperatureOffset",
            payload=load_json_value_fixture(device_temp_offset),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones",
            payload=load_json_value_fixture(zones_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zoneStates",
            payload=load_json_value_fixture(zone_states_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/6/capabilities",
            payload=load_json_value_fixture(zone_6_capabilities_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/5/capabilities",
            payload=load_json_value_fixture(zone_5_capabilities_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/4/capabilities",
            payload=load_json_value_fixture(zone_4_capabilities_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/3/capabilities",
            payload=load_json_value_fixture(zone_3_capabilities_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/2/capabilities",
            payload=load_json_value_fixture(zone_2_capabilities_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/1/capabilities",
            payload=load_json_value_fixture(zone_1_capabilities_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/1/defaultOverlay",
            payload=load_json_value_fixture(zone_def_overlay),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/2/defaultOverlay",
            payload=load_json_value_fixture(zone_def_overlay),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/3/defaultOverlay",
            payload=load_json_value_fixture(zone_def_overlay),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/4/defaultOverlay",
            payload=load_json_value_fixture(zone_def_overlay),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/5/defaultOverlay",
            payload=load_json_value_fixture(zone_def_overlay),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/6/defaultOverlay",
            payload=load_json_value_fixture(zone_def_overlay),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/6/state",
            payload=load_json_value_fixture(zone_6_state_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/5/state",
            payload=load_json_value_fixture(zone_5_state_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/4/state",
            payload=load_json_value_fixture(zone_4_state_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/3/state",
            payload=load_json_value_fixture(zone_3_state_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/2/state",
            payload=load_json_value_fixture(zone_2_state_fixture),
        )
        m.get(
            "https://my.tado.com/api/v2/homes/1/zones/1/state",
            payload=load_json_value_fixture(zone_1_state_fixture),
        )

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_USERNAME: "mock", CONF_PASSWORD: "mock"},
            options={"fallback": "NEXT_TIME_BLOCK"},
        )
        entry.add_to_hass(hass)

        if not skip_setup:
            await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()
