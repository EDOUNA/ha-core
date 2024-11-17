"""The sensor tests for the tado platform."""

import logging

import aioresponses
from tadoasync import Tado

from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant

from .util import async_init_integration

from tests.components.tado.util_new import async_init_integration_second

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


async def test_heater_create_binary_sensors(hass: HomeAssistant) -> None:
    """Test creation of heater sensors."""

    await async_init_integration(hass)

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


async def test_water_heater_create_binary_sensors(hass: HomeAssistant) -> None:
    """Test creation of water heater sensors."""

    await async_init_integration(hass)

    state = hass.states.get("binary_sensor.water_heater_connectivity")
    assert state.state == STATE_ON

    state = hass.states.get("binary_sensor.water_heater_overlay")
    assert state.state == STATE_OFF

    state = hass.states.get("binary_sensor.water_heater_power")
    assert state.state == STATE_ON


async def test_home_create_binary_sensors(
    hass: HomeAssistant, python_tado: Tado, responses: aioresponses
) -> None:
    """Test creation of home binary sensors."""

    await async_init_integration_second(hass, python_tado, responses)

    for state in hass.states.async_all():
        _LOGGER.debug("Entity ID: %s, State: %s", state.entity_id, state.state)

    state = hass.states.get("binary_sensor.wr1_connection_state")
    assert state.state == STATE_ON
