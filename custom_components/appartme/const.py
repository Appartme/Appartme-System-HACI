"""Constants for the Appartme integration."""

ENVIRONMENT = "prod"
if ENVIRONMENT == "prod":
    ENV_SUFIX = ""
elif ENVIRONMENT == "preprod":
    ENV_SUFIX = "-preprod"
else:
    ENV_SUFIX = f"-{ENVIRONMENT}"

DOMAIN = "appartme"
OAUTH2_AUTHORIZE = f"https://web{ENV_SUFIX}.appartme.cloud/oAuth"
OAUTH2_TOKEN = (
    f"https://appartme-service{ENV_SUFIX}.appartme.cloud/paasapi/v1/oauth/token"
)
API_URL = f"https://api{ENV_SUFIX}.appartme.cloud/paasapi/v1"
UPDATE_INTERVAL_DEFAULT = 60
UPDATE_INTERVAL_MIN = 30

# ─── Device type constants ───────────────────────────────────────────────────

DEVICE_TYPE_MM = "mm"

# ─── Tuya property mappings ──────────────────────────────────────────────────
# Maps Tuya property codes to Home Assistant platform types.
# "switch" — HA switch platform
# "light"  — HA light platform
# "sensor" — HA sensor platform (read-only measurements)

# Boolean switch properties
TUYA_SWITCH_PROPERTIES = {
    "switch_1",
    "switch_2",
    "switch_3",
    "switch_4",
    "switch_5",
    "switch_6",
    "switch",
    "switch_usb1",
    "switch_usb2",
    "switch_usb3",
    "switch_usb4",
    "switch_usb5",
    "switch_usb6",
    "child_lock",
}

# Boolean light properties (on/off Tuya lights)
TUYA_LIGHT_PROPERTIES = {
    "switch_led",
    "switch_led_1",
    "switch_led_2",
    "switch_led_3",
    "light",
}

# Numeric/read-only sensor properties
TUYA_SENSOR_PROPERTIES = {
    "temp_current": {
        "device_class": "temperature",
        "unit": "°C",
        "state_class": "measurement",
        "value_divider": 10,
    },
    "humidity_value": {
        "device_class": "humidity",
        "unit": "%",
        "state_class": "measurement",
        "value_divider": 10,
    },
    "va_temperature": {
        "device_class": "temperature",
        "unit": "°C",
        "state_class": "measurement",
        "value_divider": 10,
    },
    "va_humidity": {
        "device_class": "humidity",
        "unit": "%",
        "state_class": "measurement",
        "value_divider": 1,
    },
    "cur_current": {
        "device_class": "current",
        "unit": "mA",
        "state_class": "measurement",
        "value_divider": 1,
    },
    "cur_power": {
        "device_class": "power",
        "unit": "W",
        "state_class": "measurement",
        "value_divider": 10,
    },
    "cur_voltage": {
        "device_class": "voltage",
        "unit": "V",
        "state_class": "measurement",
        "value_divider": 10,
    },
    "battery_percentage": {
        "device_class": "battery",
        "unit": "%",
        "state_class": "measurement",
        "value_divider": 1,
    },
    "bright_value": {
        "device_class": None,
        "unit": None,
        "state_class": "measurement",
        "value_divider": 1,
    },
    "temp_value": {
        "device_class": None,
        "unit": None,
        "state_class": "measurement",
        "value_divider": 1,
    },
}
