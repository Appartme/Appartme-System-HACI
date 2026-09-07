"""Built-in shared OAuth2 client for the Appartme integration.

Users no longer need to obtain their own client_id/client_secret — the
integration ships a shared OAuth2 client. The credentials below are
Fernet-encrypted. This is obfuscation, not secrecy: the component is
public, so the client must be treated as effectively public on the
backend (redirect URI pinned to my.home-assistant.io, user login still
required to obtain a token).
"""

from cryptography.fernet import Fernet

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN, ENVIRONMENT, OAUTH2_AUTHORIZE, OAUTH2_TOKEN

_KEY_PART_1 = b"jw3L8zJ-cArhwqfCSsL3NG"
_KEY_PART_2 = b"fNhWCoqp6BoTGQaU3CyMs="

_ENCRYPTED_CREDENTIALS = {
    "prod": (
        b"gAAAAABqlm5ASqYdRcPAN9JM3Yc8KUKMKlTbFSAvwFvx9RV6NxRLBQNDncbH-udrMXA6Ky9R"
        b"4tbHI7TrcX9S3Wcz2wccQcnMlX_CbJOSo0JnZXgA8d2PJdGKAeq1i-rWGjV4Kh6MeIc2",
        b"gAAAAABqlm5AMXOPrA1MvuwZmjZ-jtTQbks6g_-Ed7ZeE5xQd4UmoHP74LhNNIz2q_pN_C-E"
        b"bSPwn4upjRrz7lNxdMyX7LIFAVq3G5eIOzIuwI0Arlu4Z5cDku4PHkMq4KtoUP4oB3Qg",
    ),
    "preprod": (
        b"gAAAAABqlm5A_xn_RDoqdb8rIUBwE_S4CvRGrCtLF9_9UqCjRxJvlIADJIwodTAqiqJOSHDI"
        b"Ql7QIP0rLsmVluOY_QsSUIWpJzvQk9w0IivvBU8t_O8mGaugG7zXD-hcUkH0S-6TbzMK",
        b"gAAAAABqlm5AfQU9NEWJgHYNT6tecMs3VhH1KgREJnR_4S19ZWP1erdubQDvb7NakgUnpheT"
        b"ILIAebEi_o6ZIyi-5YlT4xSeisl1e-cZ2zQtGGMErJTEjRoRwJfaZMAOVMtL3CO2jgSF",
    ),
}


class AppartmeOAuth2Implementation(config_entry_oauth2_flow.LocalOAuth2Implementation):
    """Built-in shared-client OAuth2 implementation."""

    @property
    def name(self) -> str:
        """Name of the implementation (default would be 'Configuration.yaml')."""
        return "Appartme"


@callback
def async_register_builtin_implementation(hass: HomeAssistant) -> None:
    """Register the built-in OAuth2 implementation. Idempotent.

    Must be called both from async_setup (so token refresh can resolve the
    implementation at runtime) and at the start of the config flow (HA does
    not call the integration's async_setup before the first-ever flow).
    """
    encrypted = _ENCRYPTED_CREDENTIALS.get(ENVIRONMENT)
    if encrypted is None:
        return

    fernet = Fernet(_KEY_PART_1 + _KEY_PART_2)
    config_entry_oauth2_flow.async_register_implementation(
        hass,
        DOMAIN,
        AppartmeOAuth2Implementation(
            hass,
            DOMAIN,
            fernet.decrypt(encrypted[0]).decode(),
            fernet.decrypt(encrypted[1]).decode(),
            OAUTH2_AUTHORIZE,
            OAUTH2_TOKEN,
        ),
    )
