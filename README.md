# Appartme System - Home Assistant Custom Integration

The **Appartme** integration allows you to interact with your Appartme System by communicating with the Main Module through the Appartme PaaS API.

**Important:** This integration is dedicated to Appartme Systems with the Main Module. It will **not work** with legacy hardware such as Connect, Relay, or Sensor. If you wish to upgrade to the new version of the Appartme System, please contact [Appartme Support](mailto:support@appartme.com).

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
- **Main Module added to your account**: Ensure that your Main Module (the central control unit of your Appartme System) is properly set up and linked to your Appartme account.
- **OAuth Client ID and OAuth Secret**: You can request these credentials via the [Appartme OAuth Credentials Request Form](https://tally.so/r/w5vP0d).

## Configuration

To set up the Appartme integration:

1. [Click Here][integration-config] to directly add a `Appartme System` integration **or**
> - In the Home Assistant UI, click on **Settings**.
> - Select **Devices & Services** from the sidebar.
> - Click the **Add Integration** button in the bottom right corner.
> - Search for **Appartme** and select it from the list.
2. Enter your **OAuth Client ID** and **OAuth Secret** when prompted.
3. Follow the on-screen instructions to complete the setup process.
4. Once completed, you should see the Appartme integration listed in your Integrations page, and the associated devices and entities should be available in Home Assistant.

## Capabilities

This integration allows you to:

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

## Entities

The integration will create the following entities in Home Assistant:

### Climate

- **Climate Entity**: `climate.thermostat`
  - **HVAC Modes**: `heat` (only mode supported)
  - **Preset Modes**:
    - `comfort`: For regular heating schedules.
    - `eco`: For energy-saving heating schedules.
  - **Attributes**:
    - **Current Temperature**: Displays the current room temperature.
    - **Target Temperature**: Set the desired temperature for the current preset mode.

### Switches

- **Switch Entity**: `switch.lighting`

  - Control your lighting.

- **Switch Entity**: `switch.sockets`

  - Control power to your sockets.

- **Switch Entity**: `switch.water`

  - Open or close your water valve.

- **Switch Entity**: `switch.additional_channel`
  - Control the additional channel connected to your Main Module.

### Sensors

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

## Configuration Options

After the initial setup, you can adjust the following options:

- **Update Interval**: Set the frequency (in seconds) at which the integration polls the Appartme API for updates. By default **Update Interval** is set to 60 seconds, which in our opinion is enough to enjoy responsive device state updating, but you can lower it to 30 seconds if needed.

To change options:

1. Go to **Settings** > **Devices & Services**.
2. Find the Appartme integration and click on **Configure**.
3. Adjust the **Update Interval** as needed.

## Troubleshooting

### Integration Not Working with Legacy Hardware

Ensure you are using the Main Module. Legacy hardware such as Connect, Relay, or Sensor is not supported. To upgrade your system, please contact [Appartme Support](mailto:support@appartme.com).

### Entities Not Appearing

- Verify that your OAuth credentials are correct.
- Ensure that the Main Module is properly connected to your Appartme account.
- Check the Home Assistant logs for any errors during setup.

### Incorrect Readings

- Try restarting Home Assistant.
- Increase the update interval in the configuration options.
- Ensure that your Main Module is functioning correctly.

## Frequently Asked Questions

### How do I obtain OAuth credentials?

You can request your OAuth Client ID and OAuth Secret by visiting the [Appartme OAuth Credentials Request Form](https://tally.so/r/w5vP0d) and following the instructions provided.

### Can I use this integration with legacy Appartme hardware?

No, this integration is only compatible with the Appartme Main Module. It does not support legacy hardware such as Connect, Relay, or Sensor. To upgrade your system, please contact [Appartme Support](mailto:support@appartme.com).

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
