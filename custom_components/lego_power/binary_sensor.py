"""Binary sensor platform for the LEGO Power integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    """Set up the LEGO Power binary sensors."""
    async_add_entities([LegoPowerConnectedSensor(entry.runtime_data)])


class LegoPowerConnectedSensor(LegoPowerEntity, BinarySensorEntity):
    """Reports whether the hub is currently connected."""

    _attr_translation_key = "connected"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, hub) -> None:
        """Initialise the connectivity sensor."""
        super().__init__(hub)
        self._attr_unique_id = f"{hub.address}_connected"

    @property
    def is_on(self) -> bool:
        """Return True when the hub is connected."""
        return self._hub.connected
