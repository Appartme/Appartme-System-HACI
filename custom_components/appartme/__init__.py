"""Appartme Integration."""

from datetime import timedelta
from functools import reduce
import json
import logging
import os
from typing import Any

from appartme_paas import AppartmePaasClient

from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_URL, DEVICE_TYPE_MM, DOMAIN, UPDATE_INTERVAL_DEFAULT
from .coordinator import AppartmeDataUpdateCoordinator, TuyaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.LIGHT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.VALVE,
]


def read_translation_file(translation_file: str) -> dict:
    """Read the translation file synchronously."""
    with open(translation_file, encoding="utf8") as file:
        return json.load(file)


def get_translation(
    translations: dict[str, Any], translation_key: str, default_name="", **kwargs
) -> str:
    """Fetch the translated entry with formatting."""
    translation_template = reduce(
        lambda d, key: (
            d.get(key, default_name) if isinstance(d, dict) else default_name
        ),
        translation_key.split("."),
        translations,
    )

    # Ensure it's a string
    if not isinstance(translation_template, str):
        return str(translation_template)

    return translation_template.format(**kwargs)


async def async_setup_entry(hass, config_entry):
    """Set up Appartme integration from a config entry.

    Args:
        hass: Home Assistant instance.
        config_entry: The configuration entry.

    Returns:
        True if setup was successful.

    """
    # Access the update interval from options, default to 60 seconds
    update_interval = config_entry.options.get(
        "update_interval", UPDATE_INTERVAL_DEFAULT
    )

    # Fetch translations for the current language using a relative path
    language = hass.config.language
    component_directory = os.path.dirname(__file__)
    translation_file = os.path.join(
        component_directory, f"translations/{language}.json"
    )

    if not os.path.exists(translation_file):
        _LOGGER.warning(
            "Translation file for language '%s' not found at path: %s, switching to english",
            language,
            translation_file,
        )
        translation_file = os.path.join(component_directory, "translations/en.json")

    # Read the translation file in an executor to avoid blocking the event loop
    try:
        translations = await hass.async_add_executor_job(
            read_translation_file, translation_file
        )
    except FileNotFoundError:
        _LOGGER.warning("Couldn't load translations")
        translations = {}

    session = async_get_clientsession(hass)
    access_token = config_entry.data["token"]["access_token"]
    api = AppartmePaasClient(access_token, session=session, api_url=API_URL)

    devices = await api.fetch_devices()
    devices_info = []
    tuya_devices_info = []
    coordinators = {}

    for device in devices:
        device_id = device["deviceId"]
        device_type = device.get("type", "")

        if device_type == DEVICE_TYPE_MM:
            # ── Main Module (MM) device ──────────────────────────────────
            device_info = await api.fetch_device_details(device_id)
            if device_info is None:
                _LOGGER.warning(
                    "Could not fetch details for MM device %s. Skipping",
                    device_id,
                )
                continue

            devices_info.append(device_info)

            default_device_name = get_translation(
                translations, "device.default_name", "Main Module"
            )

            coordinator = AppartmeDataUpdateCoordinator(
                hass,
                api,
                device_id,
                device_info.get("name", default_device_name),
                update_interval=timedelta(seconds=update_interval),
            )

            try:
                await coordinator.async_config_entry_first_refresh()
            except ConfigEntryNotReady as err:
                _LOGGER.warning(
                    "Initial data fetch failed for MM device %s: %s", device_id, err
                )
            except Exception as err:  # noqa: BLE001
                _LOGGER.error(
                    "Unexpected error during initial data fetch for MM device %s: %s",
                    device_id,
                    err,
                )

            coordinators[device_id] = coordinator

        else:
            # ── Tuya device (non-MM) ─────────────────────────────────────
            try:
                device_info = await api.fetch_device_details(device_id)
                if device_info is None:
                    _LOGGER.warning(
                        "Could not fetch details for Tuya device %s. Skipping",
                        device_id,
                    )
                    continue

                tuya_devices_info.append(device_info)

                device_name = device_info.get("name") or device.get("name", f"Tuya {device_id[:8]}")
                device_model = device_info.get("type", device_type)

                coordinator = TuyaDataUpdateCoordinator(
                    hass,
                    api,
                    device_id,
                    device_name,
                    device_model,
                    update_interval=timedelta(seconds=update_interval),
                )

                try:
                    await coordinator.async_config_entry_first_refresh()
                except ConfigEntryNotReady as err:
                    _LOGGER.warning(
                        "Initial data fetch failed for Tuya device %s: %s",
                        device_id,
                        err,
                    )
                except Exception as err:  # noqa: BLE001
                    _LOGGER.error(
                        "Unexpected error during initial data fetch for Tuya device %s: %s",
                        device_id,
                        err,
                    )

                coordinators[device_id] = coordinator

            except Exception as err:  # noqa: BLE001
                _LOGGER.warning(
                    "Failed to set up Tuya device %s: %s. Skipping",
                    device_id,
                    err,
                )

    # Store the devices and coordinators in hass.data for use in other platforms
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = {
        "devices_info": devices_info,
        "tuya_devices_info": tuya_devices_info,
        "api": api,
        "translations": translations,
        "coordinators": coordinators,
    }

    # Forward the setup to the individual platforms
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass, config_entry):
    """Unload Appartme integration from a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)
    return unload_ok
