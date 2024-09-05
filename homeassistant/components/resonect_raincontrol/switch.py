import json
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.components import mqtt
from homeassistant.helpers.event import async_track_time_interval, async_call_later


from datetime import timedelta

from .const import DOMAIN, TOPIC

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up the switch platform."""
    switch = ValveSwitch(hass, "Valve Switch", "api/v1/valve")
    async_add_entities([switch], update_before_add=True)


class ValveSwitch(SwitchEntity):
    """Representation of a switch."""

    def __init__(self, hass, name, topic):
        self.hass = hass
        self._name = name
        self._state = False
        self._topic = topic

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._state

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        self._state = True
        await self._publish_mqtt(1, json.dumps({"valve": True}))
        self.schedule_update_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        self._state = False
        await self._publish_mqtt(0, json.dumps({"valve": False}))
        self.schedule_update_ha_state()

    async def _publish_mqtt(self, mode, message):
        """Publish a message to the MQTT topic."""
        topic = self._topic
        if mode == 0:
            topic += "/off"
        elif mode == 1:
            topic += "/on"

        await mqtt.async_publish(self.hass, topic, message)


async def start_demo_mode(hass: HomeAssistant):
    """Start the demo mode, periodically opening and closing the valve."""

    @callback
    async def toggle_valve(now):
        # Get the switch entity
        switch = hass.data[DOMAIN].get("valve_switch")
        if switch.is_on:
            await switch.async_turn_off()
            _LOGGER.info("Demo Mode: Valve closed.")
        else:
            await switch.async_turn_on()
            _LOGGER.info("Demo Mode: Valve opened.")

    # Set up periodic valve operation every 30 seconds
    remove_callback = async_track_time_interval(
        hass, toggle_valve, timedelta(seconds=30)
    )

    # Store the callback for stopping the demo mode
    hass.data[DOMAIN]["stop_demo_mode"] = remove_callback


async def stop_demo_mode(hass: HomeAssistant):
    """Stop the demo mode."""
    remove_callback = hass.data[DOMAIN].pop("stop_demo_mode", None)
    if remove_callback:
        remove_callback()
        _LOGGER.info("Demo Mode: Stopped.")
