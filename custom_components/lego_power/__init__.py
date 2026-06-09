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
    CONF_DIRECTION,
    CONF_PORT,
    CONF_SPEED,
    CONF_STOP_ACTION,
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
    options = {**entry.data, **entry.options}

    direction = options.get(CONF_DIRECTION, DEFAULT_DIRECTION)
    brake_on_stop = options.get(CONF_STOP_ACTION, DEFAULT_STOP_ACTION) == STOP_BRAKE

    hub = LegoPowerHub(
        hass,
        address=address,
        name=entry.title,
        port=int(options.get(CONF_PORT, DEFAULT_PORT)),
        speed=int(options.get(CONF_SPEED, DEFAULT_SPEED)),
        reverse=direction == DIRECTION_REVERSE,
        brake_on_stop=brake_on_stop,
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
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: LegoPowerConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await entry.runtime_data.async_disconnect()
    return unload_ok


async def _async_update_listener(
    hass: HomeAssistant, entry: LegoPowerConfigEntry
) -> None:
    """Reload the entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)
