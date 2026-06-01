"""Support for Appartme thermostat control functionality."""

import logging

from homeassistant.components import logbook
from homeassistant.components.climate import (
    PRESET_COMFORT,
    PRESET_ECO,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import get_translation
from .const import (
    DOMAIN,
    TUYA_CLIMATE_MODE,
    TUYA_CLIMATE_TEMP_CURRENT,
    TUYA_CLIMATE_TEMP_SET,
    TUYA_CLIMATE_VALUE_DIVIDER,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Appartme climate platform."""
    # Access the devices and API from hass.data
    data = hass.data[DOMAIN][config_entry.entry_id]
    devices_info = data["devices_info"]
    tuya_devices_info = data.get("tuya_devices_info", [])
    api = data["api"]
    translations = data["translations"]
    coordinators = data["coordinators"]

    # Create climate entities for the thermostat
    thermostats = []

    # ── MM thermostats ───────────────────────────────────────────────────
    for device_info in devices_info:
        device_id = device_info["deviceId"]
        coordinator = coordinators.get(device_id)
        if not coordinator:
            _LOGGER.warning("No coordinator found for device %s. Skipping", device_id)
            continue

        thermostats.extend(
            [
                AppartmeThermostat(
                    api,
                    prop["propertyId"],
                    coordinator,
                    translations,
                )
                for prop in device_info.get("properties", [])
                if prop["propertyId"] == "thermostat_mode"
            ]
        )

    # ── Tuya thermostats (e.g. TRV radiator valves) ─────────────────────
    for device_info in tuya_devices_info:
        device_id = device_info["deviceId"]
        coordinator = coordinators.get(device_id)
        if not coordinator:
            _LOGGER.warning("No coordinator found for Tuya device %s. Skipping", device_id)
            continue

        properties = device_info.get("properties", [])
        prop_ids = {p["propertyId"] for p in properties}

        # A Tuya thermostat has temp_set (readwrite) — optionally temp_current and mode
        if TUYA_CLIMATE_TEMP_SET in prop_ids:
            # Find mode values if mode property exists
            mode_prop = next(
                (p for p in properties if p["propertyId"] == TUYA_CLIMATE_MODE),
                None,
            )
            mode_values = mode_prop.get("values", []) if mode_prop else []

            thermostats.append(
                TuyaThermostat(
                    api,
                    coordinator,
                    has_temp_current=TUYA_CLIMATE_TEMP_CURRENT in prop_ids,
                    has_mode=mode_prop is not None,
                    mode_values=mode_values,
                )
            )

    if not thermostats:
        _LOGGER.debug("No thermostat entities to add")
        return

    # Add the thermostat entities to Home Assistant
    async_add_entities(thermostats)


class AppartmeThermostat(CoordinatorEntity, ClimateEntity):
    """Representation of an Appartme thermostat."""

    def __init__(self, api, property_id, coordinator, translations):
        """Initialize the thermostat."""
        super().__init__(coordinator)
        self._api = api
        self._device_id = coordinator.device_id
        self._device_name = coordinator.device_name
        self._property_id = property_id
        self._attr_translation_key = property_id
        self._attr_has_entity_name = True
        self._translations = translations

        # Optimistic state attributes
        self._attr_preset_mode = None
        self._attr_target_temperature = None

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
            "model": "Main Module",
            "sw_version": self._device_id,
        }

    @property
    def unique_id(self) -> str:
        """Return a unique ID for this entity."""
        return f"{self._device_id}_{self._property_id}"

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available HVAC operation modes."""
        return [HVACMode.HEAT]  # Only HEAT mode is supported

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current HVAC mode."""
        return HVACMode.HEAT

    @property
    def preset_modes(self) -> list[str]:
        """Return the available preset modes."""
        return [PRESET_ECO, PRESET_COMFORT]

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        # Because of optimistic update state
        if self._attr_preset_mode is not None:
            return self._attr_preset_mode

        data = self.coordinator.data
        if data is None:
            return None
        for prop in data.get("values", []):
            if prop["propertyId"] == "thermostat_mode":
                mode = prop["value"]
                if mode == "eco":
                    return PRESET_ECO
                if mode == "comfort":
                    return PRESET_COMFORT
        return None

    @property
    def current_temperature(self) -> float | None:
        """Return the current room temperature."""
        data = self.coordinator.data
        if data is None:
            return None
        for prop in data.get("values", []):
            if prop["propertyId"] == "current_temperature":
                return float(prop["value"])
        return None

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return UnitOfTemperature.CELSIUS

    @property
    def target_temperature(self) -> float | None:
        """Return the current target temperature based on the preset mode."""
        # Because of optimistic update state
        if self._attr_target_temperature is not None:
            return self._attr_target_temperature

        data = self.coordinator.data
        if data is None:
            return None

        preset_mode = self.preset_mode
        if preset_mode == PRESET_ECO:
            property_id = "eco_temperature"
        elif preset_mode == PRESET_COMFORT:
            property_id = "comfort_temperature"
        else:
            return None

        for prop in data.get("values", []):
            if prop["propertyId"] == property_id:
                return float(prop["value"])
        return None

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature that can be set."""
        # You can adjust these values or fetch from data if available
        return 10.0

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature that can be set."""
        # You can adjust these values or fetch from data if available
        return 30.0

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return the supported features."""
        return ClimateEntityFeature.PRESET_MODE | ClimateEntityFeature.TARGET_TEMPERATURE

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new HVAC mode (No actual change since only HEAT is supported)."""
        if hvac_mode != HVACMode.HEAT:
            _LOGGER.error("Only HEAT mode is supported")
            return
        # No action needed; only HEAT mode is supported
        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode):
        """Set new preset mode (eco or comfort)."""
        if preset_mode == PRESET_ECO:
            value = "eco"
        elif preset_mode == PRESET_COMFORT:
            value = "comfort"
        else:
            _LOGGER.error("Invalid preset mode: %s", preset_mode)
            return

        try:
            await self._api.set_device_property_value(self._device_id, "thermostat_mode", value)
            # Optimistically update the preset mode
            self._attr_preset_mode = preset_mode

            # Log the change with translations
            logbook.async_log_entry(
                self.hass,
                name=f"{self.name}",
                message=get_translation(
                    self._translations,
                    "entity.climate.logbook_changed_preset_mode.name",
                    preset_mode=preset_mode,
                ),
                domain=DOMAIN,
                entity_id=self.entity_id,
            )

        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Error setting preset mode for %s: %s", self.name, err)
            # Reset the optimistic attribute
            self._attr_preset_mode = None
            # Notify the user
            self.hass.components.persistent_notification.create(
                f"Failed to set preset mode for {self.name}: {err}",
                title="Appartme System",
                notification_id=f"appartme_{self._device_id}_preset_error",
            )
        finally:
            # Force UI to refresh
            self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs):
        """Set the target temperature for the current preset mode."""
        temperature = kwargs.get("temperature")
        if temperature is None:
            _LOGGER.error("No temperature provided")
            return

        preset_mode = self.preset_mode
        if preset_mode == PRESET_ECO:
            property_id = "eco_temperature"
        elif preset_mode == PRESET_COMFORT:
            property_id = "comfort_temperature"
        else:
            _LOGGER.error("Cannot set temperature when preset mode is unknown")
            return

        try:
            await self._api.set_device_property_value(self._device_id, property_id, temperature)
            # Optimistically update the target temperature
            self._attr_target_temperature = temperature

            # Log the change with translations
            logbook.async_log_entry(
                self.hass,
                name=f"{self.name}",
                message=get_translation(
                    self._translations,
                    "entity.climate.logbook_changed_target_temperature.name",
                    temperature=temperature,
                ),
                domain=DOMAIN,
                entity_id=self.entity_id,
            )

        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Error setting temperature for %s: %s", self.name, err)
            # Reset the optimistic attribute
            self._attr_target_temperature = None
            # Notify the user
            self.hass.components.persistent_notification.create(
                f"Failed to set temperature for {self.name}: {err}",
                title="Appartme System",
                notification_id=f"appartme_{self._device_id}_temperature_error",
            )
        finally:
            # Force UI to refresh
            self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Reset optimistic attributes
        self._attr_preset_mode = None
        self._attr_target_temperature = None
        self.async_write_ha_state()


class TuyaThermostat(CoordinatorEntity, ClimateEntity):
    """Representation of an Appartme+ thermostat (e.g. TRV radiator valve).

    Tuya TRV properties:
      - temp_set (readwrite, value ÷10) — target temperature
      - temp_current (read, value ÷10) — current temperature
      - mode (enum readwrite: auto/off) — HVAC mode
    """

    def __init__(self, api, coordinator, has_temp_current, has_mode, mode_values):
        """Initialize the Tuya thermostat."""
        super().__init__(coordinator)
        self._api = api
        self._device_id = coordinator.device_id
        self._device_name = coordinator.device_name
        self._has_temp_current = has_temp_current
        self._has_mode = has_mode
        self._mode_values = [v.lower() for v in mode_values]
        self._attr_has_entity_name = True

        # Optimistic state
        self._attr_target_temperature = None
        self._optimistic_hvac_mode = None

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
        return f"tuya_{self._device_id}_climate"

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available HVAC modes."""
        modes = [HVACMode.HEAT]
        if self._has_mode and "off" in self._mode_values:
            modes.append(HVACMode.OFF)
        if self._has_mode and "auto" in self._mode_values:
            modes.append(HVACMode.AUTO)
        return modes

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current HVAC mode."""
        if self._optimistic_hvac_mode is not None:
            return self._optimistic_hvac_mode

        if not self._has_mode:
            return HVACMode.HEAT

        data = self.coordinator.data
        if data is None:
            return None

        for prop in data.get("values", []):
            if prop["propertyId"] == TUYA_CLIMATE_MODE:
                mode_val = str(prop["value"]).lower()
                if mode_val == "off":
                    return HVACMode.OFF
                if mode_val == "auto":
                    return HVACMode.AUTO
                # "comfort", "manual", etc. → HEAT
                return HVACMode.HEAT
        return HVACMode.HEAT

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if not self._has_temp_current:
            return None

        data = self.coordinator.data
        if data is None:
            return None

        for prop in data.get("values", []):
            if prop["propertyId"] == TUYA_CLIMATE_TEMP_CURRENT:
                try:
                    return round(float(prop["value"]) / TUYA_CLIMATE_VALUE_DIVIDER, 1)
                except (ValueError, TypeError):
                    return None
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        if self._attr_target_temperature is not None:
            return self._attr_target_temperature

        data = self.coordinator.data
        if data is None:
            return None

        for prop in data.get("values", []):
            if prop["propertyId"] == TUYA_CLIMATE_TEMP_SET:
                try:
                    return round(float(prop["value"]) / TUYA_CLIMATE_VALUE_DIVIDER, 1)
                except (ValueError, TypeError):
                    return None
        return None

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return 5.0

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return 35.0

    @property
    def target_temperature_step(self) -> float:
        """Return the target temperature step."""
        return 0.5

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return the supported features."""
        return ClimateEntityFeature.TARGET_TEMPERATURE

    async def async_set_hvac_mode(self, hvac_mode):
        """Set HVAC mode (auto/off → Tuya mode property)."""
        if not self._has_mode:
            _LOGGER.warning("Device %s does not support mode changes", self._device_id)
            return

        if hvac_mode == HVACMode.OFF:
            mode_value = "off"
        elif hvac_mode == HVACMode.AUTO:
            mode_value = "auto"
        else:
            mode_value = "auto"  # HEAT → auto for Tuya TRVs

        try:
            await self._api.set_device_property_value(
                self._device_id, TUYA_CLIMATE_MODE, mode_value
            )
            self._optimistic_hvac_mode = hvac_mode
            _LOGGER.debug(
                "Set Tuya TRV %s mode to %s", self._device_id, mode_value
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.error(
                "Error setting HVAC mode for %s: %s", self._device_id, err
            )
            self._optimistic_hvac_mode = None
        finally:
            self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs):
        """Set the target temperature.

        Tuya TRV expects temp_set as integer value × 10 (e.g. 21.5°C → 215).
        """
        temperature = kwargs.get("temperature")
        if temperature is None:
            _LOGGER.error("No temperature provided")
            return

        # Tuya expects raw integer value (°C × 10)
        raw_value = int(round(temperature * TUYA_CLIMATE_VALUE_DIVIDER))

        try:
            await self._api.set_device_property_value(
                self._device_id, TUYA_CLIMATE_TEMP_SET, raw_value
            )
            self._attr_target_temperature = temperature
            _LOGGER.debug(
                "Set Tuya TRV %s temp_set to %s (raw: %s)",
                self._device_id, temperature, raw_value,
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.error(
                "Error setting temperature for %s: %s", self._device_id, err
            )
            self._attr_target_temperature = None
        finally:
            self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_target_temperature = None
        self._optimistic_hvac_mode = None
        self.async_write_ha_state()
