"""Bluetooth connection manager for a single LEGO Powered Up hub."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
import logging

from bleak.exc import BleakError
from bleak_retry_connector import (
    BleakClientWithServiceCache,
    establish_connection,
)

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from . import lego
from .const import LEGO_HUB_CHARACTERISTIC_UUID, MAX_SPEED, MIN_SPEED

_LOGGER = logging.getLogger(__name__)

# How many times bleak-retry-connector retries a single connection attempt.
_CONNECT_ATTEMPTS = 3


class LegoPowerConnectionError(Exception):
    """Raised when the hub cannot be reached over Bluetooth."""


class LegoPowerHub:
    """Manage the BLE link to one LEGO hub and drive a single motor."""

    def __init__(
        self,
        hass: HomeAssistant,
        address: str,
        name: str,
        port: int,
        speed: int,
        reverse: bool,
        brake_on_stop: bool,
    ) -> None:
        """Initialise the hub controller."""
        self.hass = hass
        self.address = address
        self.name = name
        self.port = port
        self.reverse = reverse
        self.brake_on_stop = brake_on_stop
        self._speed = self._clamp_speed(speed)

        self._client: BleakClientWithServiceCache | None = None
        self._lock = asyncio.Lock()
        self._running = False
        self._should_stay_connected = False
        self._callbacks: set[Callable[[], None]] = set()

    @staticmethod
    def _clamp_speed(value: int) -> int:
        """Clamp a speed percentage to the supported range."""
        return max(MIN_SPEED, min(MAX_SPEED, int(value)))

    @property
    def speed(self) -> int:
        """Return the configured run speed as a percentage (1-100)."""
        return self._speed

    @property
    def signed_power(self) -> int:
        """Return the motor power (-100..100) including direction."""
        return -self._speed if self.reverse else self._speed

    @property
    def connected(self) -> bool:
        """Return True when an active BLE connection exists."""
        return self._client is not None and self._client.is_connected

    @property
    def is_running(self) -> bool:
        """Return True when the motor has been commanded to run."""
        return self._running and self.connected

    @property
    def should_stay_connected(self) -> bool:
        """Return True when the hub is meant to maintain a connection."""
        return self._should_stay_connected

    def register_callback(self, callback: Callable[[], None]) -> Callable[[], None]:
        """Register a listener to be notified of state changes."""
        self._callbacks.add(callback)

        def _remove() -> None:
            self._callbacks.discard(callback)

        return _remove

    def _notify(self) -> None:
        """Notify all registered listeners that state changed."""
        for callback in list(self._callbacks):
            callback()

    def set_speed_value(self, speed: int) -> None:
        """Set the run speed without sending anything to the hub."""
        self._speed = self._clamp_speed(speed)

    async def async_set_speed(self, speed: int) -> None:
        """Set the run speed, applying it live if the motor is running."""
        self._speed = self._clamp_speed(speed)
        if self.is_running:
            await self._write(lego.set_motor_power(self.port, self.signed_power))
        self._notify()

    async def async_connect(self) -> None:
        """Establish the BLE connection to the hub."""
        async with self._lock:
            if self.connected:
                return

            ble_device = bluetooth.async_ble_device_from_address(
                self.hass, self.address, connectable=True
            )
            if ble_device is None:
                raise LegoPowerConnectionError(
                    f"LEGO hub {self.address} was not found; "
                    "is it powered on and in range?"
                )

            try:
                client = await establish_connection(
                    BleakClientWithServiceCache,
                    ble_device,
                    self.name,
                    disconnected_callback=self._handle_disconnect,
                    max_attempts=_CONNECT_ATTEMPTS,
                )
            except (BleakError, asyncio.TimeoutError) as err:
                raise LegoPowerConnectionError(
                    f"Could not connect to LEGO hub {self.address}: {err}"
                ) from err

            self._client = client
            self._should_stay_connected = True

            try:
                await client.start_notify(
                    LEGO_HUB_CHARACTERISTIC_UUID, self._handle_notification
                )
            except (BleakError, asyncio.TimeoutError):
                _LOGGER.debug(
                    "Could not subscribe to notifications on %s",
                    self.address,
                    exc_info=True,
                )

        _LOGGER.debug("Connected to LEGO hub %s (%s)", self.name, self.address)
        self._notify()

    async def async_connect_safe(self) -> None:
        """Attempt to connect, swallowing connection errors."""
        try:
            await self.async_connect()
        except LegoPowerConnectionError as err:
            _LOGGER.debug("Connect attempt for %s failed: %s", self.address, err)

    async def async_disconnect(self) -> None:
        """Stop the motor and disconnect, and stay disconnected."""
        self._should_stay_connected = False
        async with self._lock:
            client = self._client
            self._client = None
            self._running = False
            if client is not None and client.is_connected:
                try:
                    await client.write_gatt_char(
                        LEGO_HUB_CHARACTERISTIC_UUID,
                        lego.stop_motor(self.port, brake=self.brake_on_stop),
                        response=False,
                    )
                except (BleakError, asyncio.TimeoutError):
                    _LOGGER.debug("Error stopping motor on disconnect", exc_info=True)
                try:
                    await client.disconnect()
                except (BleakError, asyncio.TimeoutError):
                    _LOGGER.debug("Error during disconnect", exc_info=True)
        self._notify()

    async def async_set_running(self, running: bool) -> None:
        """Start or stop the motor."""
        if running:
            if not self.connected:
                await self.async_connect()
            await self._write(lego.set_motor_power(self.port, self.signed_power))
            self._running = True
        else:
            if self.connected:
                await self._write(
                    lego.stop_motor(self.port, brake=self.brake_on_stop)
                )
            self._running = False
        self._notify()

    async def _write(self, data: bytes) -> None:
        """Write a raw command to the hub characteristic."""
        client = self._client
        if client is None or not client.is_connected:
            raise LegoPowerConnectionError("Not connected to the LEGO hub")
        try:
            await client.write_gatt_char(
                LEGO_HUB_CHARACTERISTIC_UUID, data, response=False
            )
        except (BleakError, asyncio.TimeoutError) as err:
            raise LegoPowerConnectionError(
                f"Failed to send command to {self.address}: {err}"
            ) from err

    def _handle_disconnect(self, _client: BleakClientWithServiceCache) -> None:
        """Handle an unexpected disconnect from the hub."""
        _LOGGER.debug("LEGO hub %s disconnected", self.address)
        self._client = None
        self._running = False
        self._notify()
        if self._should_stay_connected:
            self.hass.async_create_task(self.async_connect_safe())

    def _handle_notification(self, _sender: int, data: bytearray) -> None:
        """Handle inbound notifications from the hub.

        Notifications are currently only used to keep the link active; the
        payloads (port info, hub alerts, etc.) are not yet interpreted.
        """
        _LOGGER.debug("Notification from %s: %s", self.address, data.hex())
