"""Appartme data coordinator."""

import logging

from appartme_paas import DeviceOfflineError

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)


class AppartmeDataUpdateCoordinator(DataUpdateCoordinator):
    """DataUpdateCoordinator to manage fetching data from Appartme API for MM devices."""

    def __init__(
        self,
        hass,
        api,
        device_id,
        device_name,
        update_interval,
    ):
        """Initialize the coordinator."""
        self.api = api
        self.device_id = device_id
        self.device_name = device_name
        self.device_type = "mm"
        super().__init__(
            hass,
            _LOGGER,
            name=f"Appartme device {device_id}",
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            return await self.api.get_device_properties(self.device_id)
        except DeviceOfflineError as err:
            self.logger.warning("Device %s is offline: %s", self.device_id, err)
            # Raise UpdateFailed to indicate the update failed
            raise UpdateFailed(f"Device {self.device_id} is offline") from err
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(
                f"Error fetching data for device {self.device_id}: {err}"
            ) from err


class TuyaDataUpdateCoordinator(DataUpdateCoordinator):
    """DataUpdateCoordinator to manage fetching data from Appartme API for Tuya devices."""

    def __init__(
        self,
        hass,
        api,
        device_id,
        device_name,
        device_model,
        update_interval,
    ):
        """Initialize the Tuya coordinator."""
        self.api = api
        self.device_id = device_id
        self.device_name = device_name
        self.device_type = "tuya"
        self.device_model = device_model
        super().__init__(
            hass,
            _LOGGER,
            name=f"Appartme Tuya device {device_id}",
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch all properties from Tuya device via Appartme PaaS API."""
        try:
            return await self.api.get_device_properties(self.device_id)
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(
                f"Error fetching data for Tuya device {self.device_id}: {err}"
            ) from err
