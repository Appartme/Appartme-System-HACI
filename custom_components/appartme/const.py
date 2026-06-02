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
    "switch_alarm_sound",
    "window_check",
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
        "value_divider": 10,
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
    "temp_set": {
        "device_class": "temperature",
        "unit": "°C",
        "state_class": "measurement",
        "value_divider": 10,
    },
}

# ─── Tuya climate (thermostat) property mappings ─────────────────────────────
# Devices that have temp_set (readwrite) + temp_current (read) are thermostats.
# The integration creates a Climate entity for these.

TUYA_CLIMATE_TEMP_SET = "temp_set"       # target temperature (÷10)
TUYA_CLIMATE_TEMP_CURRENT = "temp_current"  # current temperature (÷10)
TUYA_CLIMATE_MODE = "mode"               # enum: auto, off (and others)
TUYA_CLIMATE_VALUE_DIVIDER = 10

# ─── Tuya binary sensor property mappings ────────────────────────────────────
# Boolean read-only properties exposed as HA binary_sensor.
# For enum DPs, value_map is REQUIRED — never guess from value order.

TUYA_BINARY_SENSOR_PROPERTIES = {
    "doorcontact_state": {
        "device_class": "door",
        "name": "Door/Window Contact",
    },
    "window_state": {
        "device_class": "window",
        "name": "Window State",
        "value_map": {"opened": True, "closed": False},  # enum → bool
    },
    "smoke_sensor_status": {
        "device_class": "smoke",
        "name": "Smoke",
        # On = smoke detected. Off = clear.
        "value_map": {"alarm": True, "normal": False},
    },
    "battery_state": {
        "device_class": "battery",
        "name": "Battery",
        # HA battery binary_sensor convention: On = low battery alert.
        "value_map": {"low": True, "high": False},
    },
}

# ─── Tuya cover property mappings ────────────────────────────────────────────
# DPs that are claimed by the cover platform. Sensor + binary_sensor platforms
# must skip these so we don't get duplicate entities for the same physical
# concept (position, motion direction).

TUYA_PROPERTIES_CONSUMED_BY_COVER = {
    "control",
    "percent_control",
    "percent_state",
    "work_state",
    "position",
    "mach_operate",
}
