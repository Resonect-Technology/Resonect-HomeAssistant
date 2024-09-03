import json
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.components import mqtt

from .const import DOMAIN, TOPIC


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up the switch platform."""
    switch = ValveSwitch(hass, "Valve Switch", "felix/valve")
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
        await self._publish_mqtt(json.dumps({"valve": True}))
        self.schedule_update_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        self._state = False
        await self._publish_mqtt(json.dumps({"valve": False}))
        self.schedule_update_ha_state()

    async def _publish_mqtt(self, message):
        """Publish a message to the MQTT topic."""
        await mqtt.async_publish(self.hass, self._topic, message)
