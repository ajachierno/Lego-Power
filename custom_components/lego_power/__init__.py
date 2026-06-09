"""The LEGO Power integration."""

from __future__ import annotations

import logging

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import (
    BluetoothCallbackMatcher,
    BluetoothChange,
    BluetoothServiceInfoBleak,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DEFAULT_DIRECTION,
    DEFAULT_PORT,
    DEFAULT_SPEED,
    DEFAULT_STOP_ACTION,
    DIRECTION_REVERSE,
    STOP_BRAKE,
)
from .hub import LegoPowerConnectionError, LegoPowerHub

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SWITCH,
]

type LegoPowerConfigEntry = ConfigEntry[LegoPowerHub]


async def async_setup_entry(
    hass: HomeAssistant, entry: LegoPowerConfigEntry
) -> bool:
    """Set up LEGO Power from a config entry."""
    address: str = entry.data[CONF_ADDRESS]

    # Motor port, speed, direction and stop behaviour are now controlled by
    # live entities on the device page (which restore their own state), so the
    # hub only needs sensible starting defaults here.
    hub = LegoPowerHub(
        hass,
        address=address,
        name=entry.title,
        port=DEFAULT_PORT,
        speed=DEFAULT_SPEED,
        reverse=DEFAULT_DIRECTION == DIRECTION_REVERSE,
        brake_on_stop=DEFAULT_STOP_ACTION == STOP_BRAKE,
    )

    if not bluetooth.async_address_present(hass, address, connectable=True):
        raise ConfigEntryNotReady(
            f"LEGO hub {address} is not currently in Bluetooth range"
        )

    try:
        await hub.async_connect()
    except LegoPowerConnectionError as err:
        raise ConfigEntryNotReady(str(err)) from err

    entry.runtime_data = hub

    @callback
    def _async_on_advertisement(
        _service_info: BluetoothServiceInfoBleak,
        _change: BluetoothChange,
    ) -> None:
        """Reconnect automatically when the hub starts advertising again."""
        if hub.should_stay_connected and not hub.connected:
            hass.async_create_task(hub.async_connect_safe())

    entry.async_on_unload(
        bluetooth.async_register_callback(
            hass,
            _async_on_advertisement,
            BluetoothCallbackMatcher(address=address, connectable=True),
            bluetooth.BluetoothScanningMode.ACTIVE,
        )
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: LegoPowerConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await entry.runtime_data.async_disconnect()
    return unload_ok
