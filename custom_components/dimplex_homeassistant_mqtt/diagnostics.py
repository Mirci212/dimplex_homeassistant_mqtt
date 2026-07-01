from __future__ import annotations

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

TO_REDACT = {
    "username",
    "password",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    client = coordinator.client

    data = {
        "mqtt": {
            "connected": client.connected,
            "last_connect_time": client.last_connect_time,
            "last_disconnect_time": client.last_disconnect_time,
            "disconnect_reason": client.disconnect_reason,
            "client_id": client.client_id,
            "host": client.config.get("host"),
            "port": client.config.get("port"),
            "subscribed_topics": sorted(client.subscribed_topics),
            "pending_subscriptions": client.pending_subscriptions,
        },
        "gateway": {
            "device_id": coordinator.device_id,
            "cached_values": len(client.values),
        },
        "config": client.config,
    }

    return async_redact_data(data, TO_REDACT)