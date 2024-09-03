from __future__ import annotations  # noqa: D104

import asyncio
import json
import logging
import random

import voluptuous as vol

from homeassistant.components import mqtt
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN, TOPIC

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up the sensor platform."""
    flow_sensor_1 = MqttSensor(hass, "Water Flow 1", TOPIC, "flow1")
    flow_sensor_2 = MqttSensor(hass, "Water Flow 2", TOPIC, "flow2")
    current_sensor = MqttSensor(hass, "Current", TOPIC, "current")
    async_add_entities(
        [flow_sensor_1, flow_sensor_2, current_sensor], update_before_add=True
    )


class MqttSensor(SensorEntity):
    """Representation of a sensor."""

    def __init__(self, hass, name, topic, parameter):
        self.hass = hass
        self._unique_id = f"{DOMAIN}_{name.lower().replace(' ', '_')}"
        self._name = name
        self._state = None
        self._topic = topic
        self._unsubscribe = None
        self._flow_parameter = parameter

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_added_to_hass(self):
        """Subscribe to MQTT events when added to hass."""

        @callback
        def message_received(msg):
            """Handle new MQTT messages."""
            try:
                payload_dict = json.loads(msg.payload)
                flow = payload_dict.get(self._flow_parameter)

                # Update the state of the sensor (e.g., using flow1 for this example)
                self._state = flow

                # Optionally, update other entities if needed
                # hass.states.async_set(entity_flow2, flow2)
                # hass.states.async_set(entity_current, current)

                # Notify Home Assistant of state change
                self.async_write_ha_state()

            except json.JSONDecodeError:
                # Log error if necessary
                _LOGGER.error("Failed to decode JSON payload from MQTT message")

        # Subscribe to the topic
        self._unsubscribe = await mqtt.async_subscribe(
            self.hass, self._topic, message_received
        )

    async def async_will_remove_from_hass(self):
        """Unsubscribe from MQTT events when removed from hass."""
        if self._unsubscribe is not None:
            self._unsubscribe()
