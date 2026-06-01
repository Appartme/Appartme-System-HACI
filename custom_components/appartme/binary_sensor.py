"""Support for Appartme+ binary sensors (door/window contacts)."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    TUYA_BINARY_SENSOR_PROPERTIES,
    TUYA_PROPERTIES_CONSUMED_BY_COVER,
)

_LOGGER = logging.getLogger(__name__)

DEVICE_CLASS_MAP = {
    "door": BinarySensorDeviceClass.DOOR,
    "window": BinarySensorDeviceClass.WINDOW,
    "smoke": BinarySensorDeviceClass.SMOKE,
    "battery": BinarySensorDeviceClass.BATTERY,
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Appartme+ binary sensor platform."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    tuya_devices_info = data.get("tuya_devices_info", [])
    api = data["api"]
    coordinators = data["coordinators"]

    entities = []

    for device_info in tuya_devices_info:
        device_id = device_info["deviceId"]
        coordinator = coordinators.get(device_id)
        if not coordinator:
            _LOGGER.warning(
                "No coordinator found for device %s. Skipping", device_id
            )
            continue

        for prop in device_info.get("properties", []):
            prop_id = prop["propertyId"]
            prop_type = prop.get("type", "")
            prop_mode = prop.get("mode", "")

            # Cover platform owns these — don't double-expose.
            if prop_id in TUYA_PROPERTIES_CONSUMED_BY_COVER:
                continue

            if prop_id in TUYA_BINARY_SENSOR_PROPERTIES:
                # Known binary sensor with explicit device_class and value_map.
                sensor_config = TUYA_BINARY_SENSOR_PROPERTIES[prop_id]
                entities.append(
                    TuyaBinarySensor(
                        api,
                        prop_id,
                        coordinator,
                        sensor_config=sensor_config,
                    )
                )
            elif prop_type == "boolean" and prop_mode == "read":
                # Fallback for boolean read-only — semantics are clear (True/False).
                entities.append(
                    TuyaBinarySensor(
                        api,
                        prop_id,
                        coordinator,
                        sensor_config={"device_class": None, "name": prop_id.replace("_", " ").title()},
                    )
                )
            # No fallback for enum DPs: positional value→bool mapping silently
            # inverts safety-critical sensors (e.g. ["alarm","normal"] mapped
            # alarm→False, normal→True). Require an explicit entry in
            # TUYA_BINARY_SENSOR_PROPERTIES with value_map.

    if not entities:
        _LOGGER.debug("No Appartme+ binary sensor entities to add")
        return

    async_add_entities(entities)


class TuyaBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of an Appartme+ binary sensor (door/window contact)."""

    def __init__(self, api, property_id, coordinator, sensor_config):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._api = api
        self._device_id = coordinator.device_id
        self._device_name = coordinator.device_name
        self._property_id = property_id
        self._sensor_config = sensor_config
        self._attr_has_entity_name = True

    @property
    def available(self) -> bool:
        """Return if the entity is available."""
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        """Return device information to link this entity to a device."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Appartme",
            "model": getattr(self.coordinator, "device_model", "Appartme+ Device"),
        }

    @property
    def unique_id(self) -> str:
        """Return a unique ID for this entity."""
        return f"tuya_{self._device_id}_{self._property_id}"

    @property
    def name(self) -> str:
        """Return the display name of this sensor."""
        return self._sensor_config.get(
            "name", self._property_id.replace("_", " ").title()
        )

    @property
    def device_class(self):
        """Return the device class of this binary sensor."""
        dc = self._sensor_config.get("device_class")
        return DEVICE_CLASS_MAP.get(dc) if dc else None

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on (door open / window open)."""
        data = self.coordinator.data
        if data is None:
            return None

        for prop in data.get("values", []):
            if prop["propertyId"] == self._property_id:
                value = prop["value"]
                if value is None:
                    return None

                # Handle enum values with value_map (e.g. window_state: opened/closed)
                value_map = self._sensor_config.get("value_map")
                if value_map:
                    return value_map.get(str(value).lower(), False)

                # Handle boolean values (e.g. doorcontact_state: true/false)
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    return value.lower() == "true"
                return bool(value)
        return None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
