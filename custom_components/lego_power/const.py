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
CONF_SPEED = "speed"
CONF_DIRECTION = "direction"
CONF_STOP_ACTION = "stop_action"

# Direction values.
DIRECTION_FORWARD = "forward"
DIRECTION_REVERSE = "reverse"

# Stop behaviour values.
STOP_FLOAT = "float"
STOP_BRAKE = "brake"

# Defaults.
#
# These mirror the original LEGO Piano (21323) ESPHome firmware this
# integration was built from, whose "play" command was:
#   {0x08, 0x00, 0x81, 0x00, 0x11, 0x51, 0x00, 0xCE}
# 0xCE is -50 as a signed byte -> port A (0x00), 50 % power, reverse
# direction, with "stop" sending 0x00 (float). Running the piano motor at
# full speed makes the gears skip, so the default speed is deliberately 50 %.
DEFAULT_PORT = 0
DEFAULT_SPEED = 50
DEFAULT_DIRECTION = DIRECTION_REVERSE
DEFAULT_STOP_ACTION = STOP_FLOAT

# Bounds.
MIN_PORT = 0
MAX_PORT = 63
MIN_SPEED = 1
MAX_SPEED = 100
