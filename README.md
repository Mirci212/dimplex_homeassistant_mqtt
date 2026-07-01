# Dimplex MQTT

Home Assistant custom integration for Dimplex heating systems via MQTT.

The integration connects directly to a Dimplex MQTT Gateway and exposes heating system data as Home Assistant entities for monitoring, control, dashboards, and automations.

## Features

- MQTT-based communication
- Automatic entity discovery
- Sensors
- Binary sensors
- Number entities
- Select entities
- Device diagnostics
- Local network operation
- Config Flow support
- HACS compatible
- No cloud dependency

## Installation

### HACS

1. Open **HACS** in Home Assistant.
2. Navigate to **Integrations**.
3. Click **Custom repositories**.
4. Add the repository URL.
5. Select **Integration** as the category.
6. Install **Dimplex MQTT**.
7. Restart Home Assistant.

### Manual Installation

Copy the integration folder:

```text
custom_components/dimplex_homeassistant_mqtt
```

to:

```text
/config/custom_components/dimplex_homeassistant_mqtt
```

Restart Home Assistant.

## Configuration

1. Navigate to:

   ```text
   Settings → Devices & Services
   ```

2. Click:

   ```text
   Add Integration
   ```

3. Search for:

   ```text
   Dimplex Home Assistant MQTT
   ```

4. Enter:

   - MQTT Host
   - Password

5. Finish the setup wizard.

## Entities

The integration automatically creates entities based on values received from the Dimplex MQTT Gateway.

Examples include:

- Temperature sensors
- Heating circuit values
- Operating modes
- Compressor status
- Alarm states
- Setpoints
- Read/write parameters

Available entities depend on the connected Dimplex system and gateway configuration.

## Diagnostics

Diagnostics can be downloaded from:

```text
Settings → Devices & Services
→ Dimplex Home Assistant MQTT
→ Download Diagnostics
```

The diagnostics report contains:

- MQTT connection status
- Client ID
- Subscribed topics
- Device information
- Configuration details (sensitive information is redacted)

## Requirements

- Home Assistant
- Dimplex MQTT Gateway
- Network connectivity between Home Assistant and the gateway

## Troubleshooting

### MQTT Connection Issues

Verify:

- MQTT broker is running
- Host and password are valid
- Network connectivity is available
- Firewall rules allow MQTT traffic

### Missing Entities

Verify:

- The heatpump configuration is complete
- The integration is connected

Check Home Assistant logs for additional information.

## Contributing

Bug reports, feature requests, and pull requests are welcome.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

**Dimplex Home Assistant MQTT** provides seamless integration between Dimplex heating systems and Home Assistant through reliable local MQTT communication.
