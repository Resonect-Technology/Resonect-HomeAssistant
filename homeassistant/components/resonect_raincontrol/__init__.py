from __future__ import annotations  # noqa: D104

import asyncio
import json
import random

import voluptuous as vol

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.typing import ConfigType

# The domain of your component. Should be equal to the name of your component.
DOMAIN = "resonect_raincontrol"

CONF_TOPIC = "topic"
DEFAULT_TOPIC = "felix/data"

# Schema to validate the configured MQTT topic
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(
                    CONF_TOPIC, default=DEFAULT_TOPIC
                ): mqtt.valid_subscribe_topic
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the MQTT async example component."""
    topic = config[DOMAIN][CONF_TOPIC]
    entity_flow1 = "felix.flow1"
    entity_flow2 = "felix.flow2"
    entity_current = "felix.current"

    # Listen to a message on MQTT.
    @callback
    def message_received(msg) -> None:
        """Receive new MQTT message has been received."""
        try:
            payload_dict = json.loads(msg.payload)

            flow1 = payload_dict.get("flow1")
            flow2 = payload_dict.get("flow2")
            current = payload_dict.get("current")
        except json.JSONDecodeError:
            # TODO: Log error
            return

        hass.states.async_set(entity_flow1, flow1)
        hass.states.async_set(entity_flow2, flow2)
        hass.states.async_set(entity_current, current)

    await hass.components.mqtt.async_subscribe(topic, message_received)

    hass.states.async_set(entity_flow1, 0)
    hass.states.async_set(entity_flow2, 0)
    hass.states.async_set(entity_current, 0)

    # Periodically update entities with random values for testing purposes
    async def update_entities_randomly():
        """Randomly update entities every 10 seconds for testing purposes."""
        while True:
            flow1 = random.randint(0, 100)  # Random value for flow1
            flow2 = random.randint(0, 100)  # Random value for flow2
            current = random.randint(0, 10)  # Random value for current

            hass.states.async_set(entity_flow1, flow1)
            hass.states.async_set(entity_flow2, flow2)
            hass.states.async_set(entity_current, current)

            await asyncio.sleep(10)  # Wait for 10 seconds before updating again

    # Start the periodic update task
    hass.loop.create_task(update_entities_randomly())

    # Service to publish a message on MQTT.
    @callback
    def set_state_service(call: ServiceCall) -> None:
        """Service to send a message."""
        hass.components.mqtt.async_publish(topic, call.data.get("new_state"))

    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, "set_state", set_state_service)

    # Return boolean to indicate that initialization was successfully.
    return True
