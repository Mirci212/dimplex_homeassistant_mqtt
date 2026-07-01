import logging

from .const import DOMAIN
from .coordinator import DimplexMqttCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor", "number"]


async def async_setup_entry(hass, entry):
    hass.data.setdefault(DOMAIN, {})

    coordinator = DimplexMqttCoordinator(
        hass,
        entry.data,
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    coordinator = hass.data[DOMAIN].pop(entry.entry_id, None)

    if coordinator is not None:
        coordinator.client.stop()

    if not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)

    return unload_ok