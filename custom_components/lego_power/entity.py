"""Base entity for the LEGO Power integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, MANUFACTURER
from .hub import LegoPowerHub


class LegoPowerEntity(Entity):
    """Common base for all LEGO Power entities."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hub: LegoPowerHub) -> None:
        """Initialise the entity."""
        self._hub = hub
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, hub.address)},
            connections={(CONNECTION_BLUETOOTH, hub.address)},
            name=hub.name,
            manufacturer=MANUFACTURER,
            model="Powered Up Hub",
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe to hub state changes."""
        self.async_on_remove(self._hub.register_callback(self.async_write_ha_state))
