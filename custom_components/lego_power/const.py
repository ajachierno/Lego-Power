"""Constants for the LEGO Power integration."""

from __future__ import annotations

DOMAIN = "lego_power"
MANUFACTURER = "LEGO"

# LEGO Wireless Protocol v3 (Powered Up) BLE identifiers.
# https://lego.github.io/lego-ble-wireless-protocol-docs/
LEGO_HUB_SERVICE_UUID = "00001623-1212-efde-1623-785feabcd123"
LEGO_HUB_CHARACTERISTIC_UUID = "00001624-1212-efde-1623-785feabcd123"
# Bluetooth SIG company identifier for "LEGO System A/S" (0x0397).
LEGO_MANUFACTURER_ID = 919

# Configuration / option keys.
CONF_PORT = "port"
CONF_POWER = "power"
CONF_DIRECTION = "direction"
CONF_STOP_ACTION = "stop_action"

# Direction values.
DIRECTION_FORWARD = "forward"
DIRECTION_REVERSE = "reverse"

# Stop behaviour values.
STOP_FLOAT = "float"
STOP_BRAKE = "brake"

# Defaults.
DEFAULT_PORT = 0
DEFAULT_POWER = 100
DEFAULT_DIRECTION = DIRECTION_FORWARD
DEFAULT_STOP_ACTION = STOP_FLOAT

# Bounds.
MIN_PORT = 0
MAX_PORT = 63
MIN_POWER = 1
MAX_POWER = 100
