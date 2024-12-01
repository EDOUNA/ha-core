"""The sensor tests for the tado platform."""

import logging
from unittest.mock import AsyncMock

from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def test_air_con_create_binary_sensors(
    hass: HomeAssistant, setup_tado_integration: None, mock_tado_client: AsyncMock
) -> None:
    """Test creation of aircon sensors."""
    state = hass.states.get("binary_sensor.air_conditioning_power")
    assert state.state == STATE_ON

    state = hass.states.get("binary_sensor.air_conditioning_connectivity")
    assert state.state == STATE_ON

    state = hass.states.get("binary_sensor.air_conditioning_overlay")
    assert state.state == STATE_ON

    state = hass.states.get("binary_sensor.air_conditioning_window")
    assert state.state == STATE_OFF


async def test_heater_create_binary_sensors(
    hass: HomeAssistant, setup_tado_integration: None, mock_tado_client: AsyncMock
) -> None:
    """Test creation of heater sensors."""
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
) -> None:
    """Test creation of water heater sensors."""
    state = hass.states.get("binary_sensor.water_heater_connectivity")
    _LOGGER.debug("Connectivity State: %s", state)

    assert state.state == STATE_ON
    state = hass.states.get("binary_sensor.water_heater_overlay")
    _LOGGER.debug("Overlay State: %s", state)

    assert state.state == STATE_OFF

    state = hass.states.get("binary_sensor.water_heater_power")
    _LOGGER.debug("Power State: %s", state)

    assert state.state == STATE_ON


async def test_home_create_binary_sensors(
    hass: HomeAssistant, setup_tado_integration: None, mock_tado_client: AsyncMock
) -> None:
    """Test creation of home binary sensors."""
    state = hass.states.get("binary_sensor.wr1_connection_state")
    assert state.state == STATE_ON
