"""config_flow platform for Appartme Integration."""

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN, UPDATE_INTERVAL_DEFAULT, UPDATE_INTERVAL_MIN
from .oauth import async_register_builtin_implementation

_LOGGER = logging.getLogger(__name__)


class AppartmeConfigFlow(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Handle a config flow for Appartme System."""

    DOMAIN = DOMAIN

    @property
    def logger(self):
        """Return logger."""
        return _LOGGER

    async def async_oauth_create_entry(self, data):
        """Create an entry after OAuth authentication."""
        if self.source == config_entries.SOURCE_REAUTH:
            return self.async_update_reload_and_abort(
                self._get_reauth_entry(), data=data
            )
        return self.async_create_entry(title="Appartme System", data=data)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        # HA does not call the integration's async_setup before the first
        # flow, so the built-in implementation must be registered here too.
        async_register_builtin_implementation(self.hass)
        return await super().async_step_user(user_input)

    async def async_step_reauth(self, entry_data):
        """Handle reauthentication if token expired or credentials revoked."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Confirm reauthentication with the user before starting OAuth."""
        if user_input is None:
            return self.async_show_form(step_id="reauth_confirm")
        return await self.async_step_user()

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Define the options flow for reconfiguration."""
        # HA 2024.12+ auto-injects `self.config_entry` on the OptionsFlow
        # instance — passing it positionally now raises TypeError.
        return AppartmeOptionsFlow()


class AppartmeOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Appartme System."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}
        if user_input is not None:
            update_interval_input = user_input.get("update_interval")
            update_interval = None
            try:
                update_interval = int(update_interval_input)
                if update_interval < UPDATE_INTERVAL_MIN:
                    errors["update_interval"] = "interval_too_short"
            except ValueError:
                errors["update_interval"] = "invalid_int"

            if not errors and update_interval is not None:
                # Save the options
                user_input["update_interval"] = (
                    update_interval  # Ensure it's stored as int
                )
                return self.async_create_entry(title="", data=user_input)

        # Get the current value or default to UPDATE_INTERVAL_DEFAULT
        current_interval = self.config_entry.options.get(
            "update_interval", UPDATE_INTERVAL_DEFAULT
        )

        # Define the options schema
        options_schema = vol.Schema(
            {vol.Required("update_interval", default=str(current_interval)): str}
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
            description_placeholders={"min_interval": UPDATE_INTERVAL_MIN},
        )
