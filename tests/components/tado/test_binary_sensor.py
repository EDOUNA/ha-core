"""The sensor tests for the tado platform."""

import logging
from unittest.mock import AsyncMock

import aioresponses
import pytest

from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant

from .util import async_init_integration

_LOGGER = logging.getLogger(__name__)


async def test_air_con_create_binary_sensors(hass: HomeAssistant) -> None:
    """Test creation of aircon sensors."""

    await async_init_integration(hass)

    state = hass.states.get("binary_sensor.air_conditioning_power")
    assert state.state == STATE_ON

    state = hass.states.get("binary_sensor.air_conditioning_connectivity")
    assert state.state == STATE_ON

    state = hass.states.get("binary_sensor.air_conditioning_overlay")
    assert state.state == STATE_ON

    state = hass.states.get("binary_sensor.air_conditioning_window")
    assert state.state == STATE_OFF


async def test_heater_create_binary_sensors(
    hass: HomeAssistant, responses: aioresponses
) -> None:
    """Test creation of heater sensors."""

    await async_init_integration_second(hass, responses)

    state = hass.states.get("binary_sensor.baseboard_heater_power")
    assert state.state == STATE_ON

    state = hass.states.get("binary_sensor.baseboard_heater_connectivity")
    assert state.state == STATE_ON

    state = hass.states.get("binary_sensor.baseboard_heater_early_start")
    assert state.state == STATE_OFF

    state = hass.states.get("binary_sensor.baseboard_heater_overlay")
    assert state.state == STATE_ON

    state = hass.states.get("binary_sensor.baseboard_heater_window")
    assert state.state == STATE_OFF


async def test_water_heater_create_binary_sensors(
    hass: HomeAssistant,
    setup_tado_integration: None,
    mock_tado_client: AsyncMock,
    mock_aiohttp_client: aioresponses,
) -> None:
    """Test creation of water heater sensors."""

    # Check the state of the water heater connectivity sensor
    state = hass.states.get("binary_sensor.water_heater_connectivity")
    _LOGGER.debug("Connectivity State: %s", state)

    assert state.state == STATE_ON

    # Check the state of the water heater overlay sensor
    state = hass.states.get("binary_sensor.water_heater_overlay")
    _LOGGER.debug("Overlay State: %s", state)

    assert state.state == STATE_OFF

    # Check the state of the water heater power sensor
    state = hass.states.get("binary_sensor.water_heater_power")
    _LOGGER.debug("Power State: %s", state)

    assert state.state == STATE_ON


@pytest.mark.asyncio
async def test_home_create_binary_sensors(
    hass: HomeAssistant, responses: aioresponses
) -> None:
    """Test creation of home binary sensors."""

    await async_init_integration_second(hass, responses)

    state = hass.states.get("binary_sensor.wr1_connection_state")
    assert state.state == STATE_ON
