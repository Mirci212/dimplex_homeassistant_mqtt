"""Sensor platform for Dimplex MQTT."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy, UnitOfTemperature, UnitOfTime
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DimplexMqttCoordinator

SENSOR_CONFIG_FILE = Path(__file__).parent / "sensors.json"
TRANSLATION_DIR = Path(__file__).parent / "translations"

DEVICE_CLASSES = {
    "temperature": SensorDeviceClass.TEMPERATURE,
    "duration": SensorDeviceClass.DURATION,
    "energy": SensorDeviceClass.ENERGY,
}

STATE_CLASSES = {
    "measurement": SensorStateClass.MEASUREMENT,
    "total": SensorStateClass.TOTAL,
    "total_increasing": SensorStateClass.TOTAL_INCREASING,
}

UNITS = {
    "celsius": UnitOfTemperature.CELSIUS,
    "C": UnitOfTemperature.CELSIUS,
    "h": UnitOfTime.HOURS,
    "hour": UnitOfTime.HOURS,
    "hours": UnitOfTime.HOURS,
    "Wh": UnitOfEnergy.WATT_HOUR,
    "wh": UnitOfEnergy.WATT_HOUR,
    "kWh": UnitOfEnergy.KILO_WATT_HOUR,
    "kwh": UnitOfEnergy.KILO_WATT_HOUR,
}


@dataclass(frozen=True, kw_only=True)
class DimplexMqttSensorEntityDescription(SensorEntityDescription):
    scale: float = 1.0


def _load_translation_file(language: str) -> dict[str, Any]:
    path = TRANSLATION_DIR / f"{language}.json"

    if not path.exists():
        path = TRANSLATION_DIR / "en.json"

    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


TRANSLATIONS = {
    "en": _load_translation_file("en"),
    "de": _load_translation_file("de"),
}


def _translate_sensor_state(
    language: str,
    translation_key: str,
    raw_value: Any,
) -> str | None:
    translations = TRANSLATIONS.get(language) or TRANSLATIONS.get("en", {})

    return (
        translations
        .get("entity", {})
        .get("sensor", {})
        .get(translation_key, {})
        .get("state", {})
        .get(str(raw_value))
    )


def _walk_sensor_config(node):
    if isinstance(node, list):
        for item in node:
            yield from _walk_sensor_config(item)
        return

    if not isinstance(node, dict):
        return

    if "id" in node:
        if node.get("read_only", True) and not str(node["id"]).endswith("d"):
            yield node
        return

    for value in node.values():
        yield from _walk_sensor_config(value)


def _load_sensor_descriptions():
    with SENSOR_CONFIG_FILE.open("r", encoding="utf-8") as file:
        config = json.load(file)

    descriptions = []

    for item in _walk_sensor_config(config):
        descriptions.append(
            DimplexMqttSensorEntityDescription(
                key=item["id"],
                translation_key=item.get("translation_key", item["key"]),
                device_class=DEVICE_CLASSES.get(item.get("device_class")),
                native_unit_of_measurement=UNITS.get(item.get("unit")),
                state_class=STATE_CLASSES.get(item.get("state_class")),
                scale=item.get("scale", 1.0),
            )
        )

    return tuple(descriptions)


SENSOR_DESCRIPTIONS = _load_sensor_descriptions()


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: DimplexMqttCoordinator = hass.data[DOMAIN][entry.entry_id]

    added: set[str] = set()

    def add_new_sensors():
        data = coordinator.data or {}
        new_entities = []

        for description in SENSOR_DESCRIPTIONS:
            if description.key in data and description.key not in added:
                added.add(description.key)
                new_entities.append(DimplexMqttSensor(coordinator, description))

        if new_entities:
            async_add_entities(new_entities)

    add_new_sensors()
    coordinator.async_add_listener(add_new_sensors)

class DimplexMqttSensor(CoordinatorEntity[DimplexMqttCoordinator], SensorEntity):
    entity_description: DimplexMqttSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DimplexMqttCoordinator,
        description: DimplexMqttSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)

        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"
        self._attr_translation_key = description.translation_key
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_id)},
            "name": "Dimplex MQTT Gateway",
            "manufacturer": "Dimplex",
            "model": "MQTT Gateway",
        }

    @property
    def available(self) -> bool:
        data = self.coordinator.data or {}
        return self.entity_description.key in data

    @property
    def native_value(self) -> Any:
        desc = self.entity_description
        data = self.coordinator.data or {}
        raw_value = data.get(desc.key)

        if raw_value is None:
            return None

        language = (self.coordinator.hass.config.language or "en").split("-")[0]

        translated = _translate_sensor_state(
            language,
            desc.translation_key,
            raw_value,
        )

        if translated is not None:
            return translated

        if desc.scale != 1.0:
            try:
                return round(float(raw_value) * desc.scale, 2)
            except (TypeError, ValueError):
                return raw_value

        return raw_value