from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up the switch platform."""
    switch = MySwitch()
    async_add_entities([switch], update_before_add=True)


class MySwitch(SwitchEntity):
    """Representation of a switch."""

    def __init__(self):
        self._state = False

    @property
    def name(self):
        """Return the name of the switch."""
        return "My Switch"

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self._state = False
        self.schedule_update_ha_state()
