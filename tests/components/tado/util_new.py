"""Test utility for Tado."""

from aioresponses import aioresponses
import pytest
from tadoasync import Tado

from homeassistant.components.tado.const import DOMAIN
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import TADO_API_URL, TADO_TOKEN_URL

from tests.common import MockConfigEntry, load_fixture


@pytest.mark.asyncio
async def async_init_integration_second(
    hass: HomeAssistant,
    python_tado: Tado,
    responses: aioresponses,
    mock_tado_client=None,
    skip_setup: bool = False,
):
    """Test the async_init_integration function."""

    responses.post(
        f"{TADO_TOKEN_URL}",
        status=200,
        payload={
            "access_token": "test_access_token",
            "expires_in": 3600,
            "refresh_token": "test_refresh_token",
        },
    )
    responses.get(
        f"{TADO_API_URL}/me",
        status=200,
        body=load_fixture("tado/me.json"),
    )

    # After this, all the devices, zones, etc. are fetched
    responses.get(
        f"{TADO_API_URL}/homes/1/devices",
        status=200,
        body=load_fixture("tado/device_wr1.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/weather",
        status=200,
        body=load_fixture("tado/weather.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/state",
        status=200,
        body=load_fixture("tado/home_state.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/devices",
        status=200,
        body=load_fixture("tado/devices.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/mobileDevices",
        status=200,
        body=load_fixture("tado/mobile_devices.json"),
    )
    responses.get(
        f"{TADO_API_URL}/devices/WR1/",
        status=200,
        body=load_fixture("tado/device_wr1.json"),
    )
    responses.get(
        f"{TADO_API_URL}/devices/WR1/temperatureOffset",
        status=200,
        body=load_fixture("tado/device_temp_offset.json"),
    )
    responses.get(
        f"{TADO_API_URL}/devices/WR4/temperatureOffset",
        status=200,
        body=load_fixture("tado/device_temp_offset.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones",
        status=200,
        body=load_fixture("tado/zones.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zoneStates",
        status=200,
        body=load_fixture("tado/zone_states.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/6/capabilities",
        status=200,
        body=load_fixture("tado/zone_with_fanlevel_horizontal_vertical_swing.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/5/capabilities",
        status=200,
        body=load_fixture("tado/zone_with_swing_capabilities.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/4/capabilities",
        status=200,
        body=load_fixture("tado/water_heater_zone_capabilities.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/3/capabilities",
        status=200,
        body=load_fixture("tado/zone_capabilities.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/2/capabilities",
        status=200,
        body=load_fixture("tado/water_heater_zone_capabilities.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/1/capabilities",
        status=200,
        body=load_fixture("tado/tadov2.zone_capabilities.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/1/defaultOverlay",
        status=200,
        body=load_fixture("tado/zone_default_overlay.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/2/defaultOverlay",
        status=200,
        body=load_fixture("tado/zone_default_overlay.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/3/defaultOverlay",
        status=200,
        body=load_fixture("tado/zone_default_overlay.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/4/defaultOverlay",
        status=200,
        body=load_fixture("tado/zone_default_overlay.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/5/defaultOverlay",
        status=200,
        body=load_fixture("tado/zone_default_overlay.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/6/defaultOverlay",
        status=200,
        body=load_fixture("tado/zone_default_overlay.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/6/state",
        status=200,
        body=load_fixture("tado/smartac4.with_fanlevel.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/5/state",
        status=200,
        body=load_fixture("tado/smartac3.with_swing.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/4/state",
        status=200,
        body=load_fixture("tado/tadov2.water_heater.heating.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/3/state",
        status=200,
        body=load_fixture("tado/smartac3.cool_mode.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/2/state",
        status=200,
        body=load_fixture("tado/tadov2.water_heater.auto_mode.json"),
    )
    responses.get(
        f"{TADO_API_URL}/homes/1/zones/1/state",
        status=200,
        body=load_fixture("tado/tadov2.heating.manual_mode.json"),
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

    assert entry.state == "loaded"
