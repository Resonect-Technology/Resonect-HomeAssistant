from __future__ import annotations  # noqa: D104

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
    entity_id = "felix.flow1"

    # Listen to a message on MQTT.
    @callback
    def message_received(msg) -> None:
        """Receive new MQTT message has been received."""
        hass.states.async_set(entity_id, msg.payload)

    await hass.components.mqtt.async_subscribe(topic, message_received)

    hass.states.async_set(entity_id, "No messages")

    # Service to publish a message on MQTT.
    @callback
    def set_state_service(call: ServiceCall) -> None:
        """Service to send a message."""
        hass.components.mqtt.async_publish(topic, call.data.get("new_state"))

    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, "set_state", set_state_service)

    # Return boolean to indicate that initialization was successfully.
    return True
