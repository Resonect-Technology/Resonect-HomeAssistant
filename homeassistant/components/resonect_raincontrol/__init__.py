import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .switch import start_demo_mode, async_setup_entry, stop_demo_mode

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration via YAML."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration via the UI."""
    _LOGGER.info("Setting up My Integration from config entry")

    await hass.config_entries.async_forward_entry_setup(entry, "switch")

    await hass.config_entries.async_forward_entry_setup(entry, "sensor")

    # Start demo mode if enabled in options
    if entry.options.get("demo_mode"):
        await start_demo_mode(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "switch")
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Update options and start/stop demo mode."""
    if entry.options.get("demo_mode"):
        await start_demo_mode(hass)
    else:
        await stop_demo_mode(hass)
        _LOGGER.info("Demo mode is disabled")
