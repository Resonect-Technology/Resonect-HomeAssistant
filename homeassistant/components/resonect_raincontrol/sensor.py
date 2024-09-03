from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up the sensor platform."""
    sensor = MySensor()
    async_add_entities([sensor], update_before_add=True)


class MySensor(SensorEntity):
    """Representation of a sensor."""

    def __init__(self):
        self._state = 0

    @property
    def name(self):
        """Return the name of the sensor."""
        return "My Sensor"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Fetch new state data for the sensor."""
        self._state += 1  # For example, increase the state by 1
