"""Switch platform for the LEGO Power integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import LegoPowerConfigEntry
from .entity import LegoPowerEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LegoPowerConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the LEGO Power switches."""
    hub = entry.runtime_data
    async_add_entities(
        [LegoPowerMotorSwitch(hub), LegoPowerConnectionSwitch(hub)]
    )


class LegoPowerMotorSwitch(LegoPowerEntity, SwitchEntity):
    """Switch that runs or stops the motor."""

    _attr_translation_key = "motor"
    _attr_icon = "mdi:engine"

    def __init__(self, hub) -> None:
        """Initialise the motor switch."""
        super().__init__(hub)
        self._attr_unique_id = f"{hub.address}_motor"

    @property
    def is_on(self) -> bool:
        """Return True when the motor is running."""
        return self._hub.is_running

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Start the motor (connecting first if needed)."""
        await self._hub.async_set_running(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Stop the motor."""
        await self._hub.async_set_running(False)


class LegoPowerConnectionSwitch(LegoPowerEntity, SwitchEntity):
    """Switch that connects or disconnects the hub over Bluetooth."""

    _attr_translation_key = "connection"
    _attr_icon = "mdi:bluetooth"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, hub) -> None:
        """Initialise the connection switch."""
        super().__init__(hub)
        self._attr_unique_id = f"{hub.address}_connection"

    @property
    def is_on(self) -> bool:
        """Return True when the hub is connected."""
        return self._hub.connected

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Connect to the hub."""
        await self._hub.async_connect_safe()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disconnect from the hub."""
        await self._hub.async_disconnect()
