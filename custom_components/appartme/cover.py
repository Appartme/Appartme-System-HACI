"""Support for Appartme+ (Tuya) curtain/cover devices."""

import logging
from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


# Tuya curtain devices come in several DP "flavours". We detect which one a
# device speaks by the set of propertyIds it exposes and drive a single
# CoverEntity off a profile dict.
#
# Position convention chosen for this integration: 100 = fully CLOSED,
# 0 = fully OPEN. The Tuya devices we support report the inverse, so the
# raw value is flipped (`100 - value`) in both directions.
COVER_PROFILES = [
    {
        # Wi-Fi Curtain Switch / MAGE10D-TYW (e.g. Tuya PID h8hit5awxfraops2)
        # Motion state is derived from `control` (the last command echoed back
        # by the device), not `work_state`. `work_state` has values only for
        # ["opening","closing"] — it sticks at the last motion direction
        # after the curtain stops, leaving HA showing "opening" forever.
        # `control` has an explicit "stop" value so we can tell when motion
        # has ended.
        "name": "tuya_curtain_switch",
        "required": {"control", "percent_control", "percent_state"},
        "command_prop": "control",
        "command_open": "open",
        "command_close": "close",
        "command_stop": "stop",
        "position_target_prop": "percent_control",
        "position_state_prop": "percent_state",
        "motion_prop": "control",
        "motion_opening": "open",
        "motion_closing": "close",
    },
    {
        # BCM700D-style curtain motor (e.g. Tuya PID XS76BY5Q1uKO6gjC)
        "name": "tuya_curtain_motor",
        "required": {"mach_operate", "position"},
        "command_prop": "mach_operate",
        "command_open": "OPEN",
        "command_close": "CLOSE",
        "command_stop": "STOP",
        "position_target_prop": "position",
        "position_state_prop": "position",
        "motion_prop": "mach_operate",
        "motion_opening": "OPEN",
        "motion_closing": "CLOSE",
    },
    {
        # Roller/curtain devices that don't report a separate state position
        # (e.g. APRM-05-005). The target value is echoed back as the only
        # position signal we have — used as both target and state.
        # Must remain LAST in the list — its requirements are a subset of
        # the curtain-switch profile above, so stricter profiles match first.
        "name": "tuya_cover_no_feedback",
        "required": {"control", "percent_control"},
        "command_prop": "control",
        "command_open": "open",
        "command_close": "close",
        "command_stop": "stop",
        "position_target_prop": "percent_control",
        "position_state_prop": "percent_control",
        "motion_prop": "control",
        "motion_opening": "open",
        "motion_closing": "close",
    },
]


def _match_profile(properties: list[dict]) -> dict | None:
    """Return the first cover profile fully satisfied by the device's DPs."""
    prop_ids = {p["propertyId"] for p in properties}
    for profile in COVER_PROFILES:
        if profile["required"].issubset(prop_ids):
            return profile
    return None


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Appartme cover platform (Tuya curtains)."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    tuya_devices_info = data.get("tuya_devices_info", [])
    api = data["api"]
    coordinators = data["coordinators"]

    covers = []

    for device_info in tuya_devices_info:
        properties = device_info.get("properties", [])
        profile = _match_profile(properties)
        if profile is None:
            continue

        device_id = device_info["deviceId"]
        coordinator = coordinators.get(device_id)
        if not coordinator:
            _LOGGER.warning(
                "No coordinator found for Tuya cover device %s. Skipping", device_id
            )
            continue

        covers.append(TuyaCover(api, coordinator, profile))

    if not covers:
        return

    async_add_entities(covers)


class TuyaCover(CoordinatorEntity, CoverEntity):
    """A Tuya curtain/blind controlled via the Appartme PaaS API."""

    _attr_device_class = CoverDeviceClass.CURTAIN
    _attr_has_entity_name = True
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
    )

    def __init__(self, api, coordinator, profile):
        """Initialize the Tuya cover entity."""
        super().__init__(coordinator)
        self._api = api
        self._profile = profile
        self._device_id = coordinator.device_id
        self._device_name = coordinator.device_name

        # Optimistic state, cleared on next coordinator refresh.
        self._optimistic_position: int | None = None
        self._optimistic_opening: bool = False
        self._optimistic_closing: bool = False

    @property
    def available(self) -> bool:
        """Return if the entity is available."""
        return self.coordinator.last_update_success

    @property
    def unique_id(self) -> str:
        """Return a unique ID for this cover."""
        return f"tuya_{self._device_id}_cover"

    @property
    def name(self) -> str | None:
        """Return None so HA uses the device name (has_entity_name=True)."""
        return None

    @property
    def device_info(self):
        """Return device information to link this entity to a Tuya device."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Appartme",
            "model": getattr(self.coordinator, "device_model", "Appartme+ Device"),
        }

    def _read_value(self, property_id: str):
        data = self.coordinator.data
        if data is None:
            return None
        for prop in data.get("values", []):
            if prop["propertyId"] == property_id:
                return prop.get("value")
        return None

    @staticmethod
    def _tuya_to_ha(value) -> int | None:
        if value is None:
            return None
        try:
            return 100 - int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _ha_to_tuya(value: int) -> int:
        return 100 - int(value)

    @property
    def current_cover_position(self) -> int | None:
        """Return the current cover position (100=closed, 0=open in this integration)."""
        if self._optimistic_position is not None:
            return self._optimistic_position
        return self._tuya_to_ha(self._read_value(self._profile["position_state_prop"]))

    @property
    def is_closed(self) -> bool | None:
        """Return True if the cover is fully closed."""
        position = self.current_cover_position
        if position is None:
            return None
        return position == 0

    @property
    def is_opening(self) -> bool:
        """Return True if the cover is currently opening."""
        if self._optimistic_opening:
            return True
        motion_prop = self._profile["motion_prop"]
        if motion_prop is None:
            return False
        return self._read_value(motion_prop) == self._profile["motion_opening"]

    @property
    def is_closing(self) -> bool:
        """Return True if the cover is currently closing."""
        if self._optimistic_closing:
            return True
        motion_prop = self._profile["motion_prop"]
        if motion_prop is None:
            return False
        return self._read_value(motion_prop) == self._profile["motion_closing"]

    async def _send(self, property_id: str, value: Any) -> None:
        try:
            await self._api.set_device_property_value(self._device_id, property_id, value)
        except Exception as err:  # noqa: BLE001
            _LOGGER.error(
                "Error setting %s=%s on cover %s: %s",
                property_id,
                value,
                self._device_name,
                err,
            )
            raise

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        await self._send(self._profile["command_prop"], self._profile["command_open"])
        self._optimistic_opening = True
        self._optimistic_closing = False
        self.async_write_ha_state()

    async def async_close_cover(self, **kwargs):
        """Close the cover."""
        await self._send(self._profile["command_prop"], self._profile["command_close"])
        self._optimistic_closing = True
        self._optimistic_opening = False
        self.async_write_ha_state()

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        await self._send(self._profile["command_prop"], self._profile["command_stop"])
        self._optimistic_opening = False
        self._optimistic_closing = False
        self.async_write_ha_state()

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = int(kwargs[ATTR_POSITION])
        await self._send(
            self._profile["position_target_prop"], self._ha_to_tuya(position)
        )
        self._optimistic_position = position
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator — drop optimistic flags."""
        self._optimistic_position = None
        self._optimistic_opening = False
        self._optimistic_closing = False
        self.async_write_ha_state()
