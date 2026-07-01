import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .mqtt_client import DimplexMqttClient

_LOGGER = logging.getLogger(__name__)


class DimplexMqttCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,
        )

        self.hass = hass
        self.device_id = config["host"]
        try:
            self.client = DimplexMqttClient(
                config,
                on_values_changed=self._handle_values_changed,
            )
        except TimeoutError as err:
            raise ConfigEntryNotReady(
                f"Dimplex MQTT broker unreachable at {config['host']}:{config['port']}"
            ) from err
        except OSError as err:
            raise ConfigEntryNotReady(
                f"Dimplex MQTT connection failed at {config['host']}:{config['port']}: {err}"
            ) from err

    def _handle_values_changed(self, changed_values: dict):
        self.hass.loop.call_soon_threadsafe(
            self._async_handle_values_changed,
            changed_values,
        )

    def _async_handle_values_changed(self, changed_values: dict):
        data = dict(self.data or {})
        data.update(changed_values)
        self.async_set_updated_data(data)

    async def _async_update_data(self):
        return self.data or {}