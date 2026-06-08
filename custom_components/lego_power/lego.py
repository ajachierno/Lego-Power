"""Helpers for building LEGO Wireless Protocol v3 messages.

Only the small subset of the protocol required to start and stop a motor on a
LEGO Powered Up hub is implemented here. See the official specification:
https://lego.github.io/lego-ble-wireless-protocol-docs/

All commands are "Port Output Commands" (message type ``0x81``) using the
``WriteDirectModeData`` sub command (``0x51``) with direct power mode (``0x00``),
which is the universal way to drive a basic motor on any Powered Up port.
"""

from __future__ import annotations

# Common message fields.
HUB_ID = 0x00
MSG_PORT_OUTPUT_COMMAND = 0x81
# Startup (execute immediately, 0x10) + completion (request feedback, 0x01).
STARTUP_AND_COMPLETION = 0x11
SUBCMD_WRITE_DIRECT_MODE_DATA = 0x51
MOTOR_POWER_MODE = 0x00

# Special power values understood by the hub.
POWER_FLOAT = 0  # Coast / let the motor spin freely.
POWER_BRAKE = 127  # Actively hold position.


def _signed_byte(value: int) -> int:
    """Return ``value`` (-128..127) as an unsigned byte (two's complement)."""
    return value & 0xFF


def _port_output(port: int, payload: bytes) -> bytes:
    """Build a Port Output / WriteDirectModeData message for ``port``."""
    body = bytes(
        [
            HUB_ID,
            MSG_PORT_OUTPUT_COMMAND,
            port & 0xFF,
            STARTUP_AND_COMPLETION,
            SUBCMD_WRITE_DIRECT_MODE_DATA,
            MOTOR_POWER_MODE,
        ]
    ) + payload
    # The first byte is the total message length, including itself.
    return bytes([len(body) + 1]) + body


def set_motor_power(port: int, power: int) -> bytes:
    """Build a command setting direct motor power (``-100``..``100``)."""
    power = max(-100, min(100, int(power)))
    return _port_output(port, bytes([_signed_byte(power)]))


def stop_motor(port: int, *, brake: bool = False) -> bytes:
    """Build a command stopping the motor (coast by default, or brake)."""
    value = POWER_BRAKE if brake else POWER_FLOAT
    return _port_output(port, bytes([_signed_byte(value)]))
