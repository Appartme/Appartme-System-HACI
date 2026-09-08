# Appartme System - Home Assistant Custom Integration

The **Appartme** integration allows you to interact with your Appartme System through the Appartme PaaS API. It supports two categories of devices:

- **Main Module (MM)** — the central control unit of your Appartme System, managing lighting, sockets, heating, water valve, energy monitoring, and more.
- **Appartme+ devices** — additional smart devices in the Appartme ecosystem (smart plugs, sensors, switches, lights, and other accessories).

Both device types are discovered automatically during setup and appear as separate devices in Home Assistant.

**Important:** This integration is dedicated to Appartme Systems with the Main Module and/or Appartme+ devices. It will **not work** with legacy hardware such as Connect, Relay, or Sensor. If you wish to upgrade to the new version of the Appartme System, please contact [Appartme Support](mailto:support@appartme.com).

## Installation

#### Method 1: Install from [HACS][hacs] (recommended)
1. Have [HACS][hacs] installed, this will allow you to easily manage and track updates.
2. Search in HACS for "Appartme System - Home Assistant Custom Integration" integration or just press the button below:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)][hacs-repository]

3. Click Install below the found integration.

#### Method 2: Manual installation
1. Using the tool of choice open the folder (directory) for your HA configuration (where you find `configuration.yaml`)
2. If you do not have a `custom_components` folder there, you need to create it
3. In the `custom_components` folder create a new folder called `appartme`
4. Download _all_ the files from the `custom_components/appartme/` folder in this repository
5. Place the files you downloaded in the new folder you created
6. *Restart HA to load the new integration*

## Prerequisites

To use this integration, you will need:

- **An Appartme account**: You can create an account using the Appartme mobile app.
- **At least one supported device linked to your account**:
  - **Main Module** — the central control unit of your Appartme System, or
  - **Appartme+ device** — an additional smart device added via the Appartme app.

> **Note:** As of version 1.2.0 you no longer need to request OAuth credentials — the integration ships with a built-in OAuth client. Advanced users can still use their own credentials via Home Assistant's **Application Credentials**.

## Configuration

To set up the Appartme integration:

1. [Click Here][integration-config] to directly add a `Appartme System` integration **or**
> - In the Home Assistant UI, click on **Settings**.
> - Select **Devices & Services** from the sidebar.
> - Click the **Add Integration** button in the bottom right corner.
> - Search for **Appartme** and select it from the list.
2. Log in with your **Appartme account** when redirected to the Appartme authorization page and approve access.
3. Once completed, you should see the Appartme integration listed in your Integrations page, and the associated devices and entities should be available in Home Assistant.

## Capabilities

### Main Module (MM)

The Main Module is the central unit of the Appartme System. Through this integration you can:

- **Control all channels connected to your Main Module**:

  - **Lighting**: Turn your lighting on or off.
  - **Sockets**: Control power to your sockets.
  - **Heating**:
    - Switch between `comfort` and `eco` modes.
    - Set target temperatures for each mode.
  - **Water Valve**: Open or close your water valve.
  - **Additional Channel**: Control an extra channel connected to your Main Module.

- **Read current temperature**:

  - Monitor the ambient temperature reported by your Main Module.

- **Change default temperature values for comfort and eco modes**:

  - Customize the default target temperatures to suit your preferences.

- **Read current voltage, current, and power information**:
  - Access real-time data on voltage, current, and power consumption for each phase and total values.

### Appartme+ Devices

Appartme+ devices are additional smart accessories in the Appartme ecosystem. The integration automatically discovers them and creates entities based on their capabilities. Supported functionality includes:

- **Switches**: Control smart plugs, relays, and multi-channel switches (up to 6 channels, USB outlets, child lock).
- **Lights**: Turn Appartme+ LED lights on or off.
- **Sensors**: Read measurements reported by Appartme+ devices:
  - **Temperature** and **Humidity** sensors.
  - **Voltage**, **Current**, and **Power** sensors.
  - **Battery level** sensors.
  - Other numeric properties are automatically exposed as generic sensors.

> **Note:** The available entities depend on the specific Appartme+ device model. The integration dynamically reads device capabilities from the Appartme API and creates only the relevant entities.

## Entities

The integration creates entities in Home Assistant grouped by device type.

### Main Module Entities

#### Climate

- **Climate Entity**: `climate.thermostat`
  - **HVAC Modes**: `heat` (only mode supported)
  - **Preset Modes**:
    - `comfort`: For regular heating schedules.
    - `eco`: For energy-saving heating schedules.
  - **Attributes**:
    - **Current Temperature**: Displays the current room temperature.
    - **Target Temperature**: Set the desired temperature for the current preset mode.

#### Switches

- **Switch Entity**: `switch.sockets` — Control power to your sockets.
- **Switch Entity**: `switch.additional_channel` — Control the additional channel connected to your Main Module.

#### Lights

- **Light Entity**: `light.lighting` — Control your lighting.

#### Valve

- **Valve Entity**: `valve.water` — Open or close your water valve.

#### Sensors

- **Sensor Entities for Each Phase**:

  - **Current Sensors**:
    - `sensor.phase_1_current`
    - `sensor.phase_2_current`
    - `sensor.phase_3_current`

  - **Voltage Sensors**:
    - `sensor.phase_1_voltage`
    - `sensor.phase_2_voltage`
    - `sensor.phase_3_voltage`

  - **Power Sensors**:
    - `sensor.phase_1_power`
    - `sensor.phase_2_power`
    - `sensor.phase_3_power`

- **Total Sensors**:
  - `sensor.total_current`
  - `sensor.total_voltage`
  - `sensor.total_power`

- **Temperature Sensor**:
  - `sensor.current_temperature`: Displays the current ambient temperature.

### Appartme+ Device Entities

Entities created for Appartme+ devices depend on the specific device model. Below are examples of commonly created entities:

#### Switches

Multi-channel switches, smart plugs, and relays will be exposed as switch entities:

- `switch.<device_name>_switch_1` — Channel 1
- `switch.<device_name>_switch_2` — Channel 2
- `switch.<device_name>_switch_3` — Channel 3
- `switch.<device_name>_child_lock` — Child lock (if supported)

#### Lights

Appartme+ LED lights will appear as light entities:

- `light.<device_name>_switch_led` — LED Light

#### Sensors

Measurement data from Appartme+ devices is exposed as sensor entities:

- `sensor.<device_name>_temp_current` — Temperature (°C)
- `sensor.<device_name>_humidity_value` — Humidity (%)
- `sensor.<device_name>_cur_power` — Power consumption (W)
- `sensor.<device_name>_cur_voltage` — Voltage (V)
- `sensor.<device_name>_cur_current` — Current (mA)
- `sensor.<device_name>_battery_percentage` — Battery level (%)

> **Note:** The exact entity names depend on the device name configured in the Appartme app and the capabilities reported by the device.

## Configuration Options

After the initial setup, you can adjust the following options:

- **Update Interval**: Set the frequency (in seconds) at which the integration polls the Appartme API for updates. By default **Update Interval** is set to 60 seconds, which in our opinion is enough to enjoy responsive device state updating, but you can lower it to 30 seconds if needed.

To change options:

1. Go to **Settings** > **Devices & Services**.
2. Find the Appartme integration and click on **Configure**.
3. Adjust the **Update Interval** as needed.

## Troubleshooting

### Integration Not Working with Legacy Hardware

Ensure you are using the Main Module or Appartme+ devices. Legacy hardware such as Connect, Relay, or Sensor is not supported. To upgrade your system, please contact [Appartme Support](mailto:support@appartme.com).

### Entities Not Appearing

- Try re-authenticating: go to **Settings** > **Devices & Services** > **Appartme**, and reload the integration or follow the re-authentication prompt if one appears.
- Ensure that the Main Module and/or Appartme+ devices are properly connected to your Appartme account.
- Check the Home Assistant logs for any errors during setup.
- For Appartme+ devices: make sure the device is online and reachable via the Appartme mobile app.

### Incorrect Readings

- Try restarting Home Assistant.
- Increase the update interval in the configuration options.
- Ensure that your Main Module or Appartme+ device is functioning correctly.

### Appartme+ Device Not Discovered

- Confirm the device is linked to your Appartme account in the mobile app.
- Restart the integration by removing and re-adding it in Home Assistant.
- Check Home Assistant logs for error messages related to device discovery.

## Frequently Asked Questions

### Do I need to obtain OAuth credentials?

No. Since version 1.2.0 the integration includes a built-in OAuth client — just add the integration and log in with your Appartme account. If you previously configured your own OAuth Client ID and Secret, your setup keeps working; when adding a new entry you can pick between your own credentials and the built-in **Appartme** option.

### Can I use this integration with legacy Appartme hardware?

No, this integration is only compatible with the Appartme Main Module and Appartme+ devices. It does not support legacy hardware such as Connect, Relay, or Sensor. To upgrade your system, please contact [Appartme Support](mailto:support@appartme.com).

### What are Appartme+ devices?

Appartme+ devices are additional smart accessories in the Appartme ecosystem — smart plugs, sensors, switches, lights, and other IoT devices managed through your Appartme account. They extend the capabilities of your Appartme System beyond the Main Module.

### How do I add an Appartme+ device?

Add the device using the Appartme mobile app. Once the device is linked to your account, it will be automatically discovered by the Home Assistant integration during setup or after reloading the integration.

### How do I change the default temperatures for comfort and eco modes?

You can adjust the default temperatures by setting the target temperature while the thermostat is in the desired preset mode (`comfort` or `eco`). The integration will then use this new temperature as the default for that mode.

## Support

If you encounter any issues or have questions:

- **Contact Appartme Support**: [support@appartme.com](mailto:support@appartme.com)
- **Home Assistant Community Forum**: [Appartme Integration Discussion](https://community.home-assistant.io/t/appartme-integration-discussion/777682)

## References

- **Appartme Official Website**: [https://www.appartme.com](https://www.appartme.com)
- **Home Assistant Developer Documentation**: [Integration Guidelines](https://developers.home-assistant.io/)

***

[hacs]: https://hacs.xyz
[hacs-repository]: https://my.home-assistant.io/redirect/hacs_repository/?owner=Appartme&repository=Appartme-System-HACI&category=integration
[integration-config]: https://my.home-assistant.io/redirect/config_flow_start/?domain=appartme
