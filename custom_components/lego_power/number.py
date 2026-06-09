"""Number platform for the LEGO Power integration."""

from __future__ import annotations

from homeassistant.components.number import NumberMode, RestoreNumber
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import LegoPowerConfigEntry
from .const import MAX_PORT, MAX_SPEED, MIN_PORT, MIN_SPEED
from .entity import LegoPowerEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LegoPowerConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the LEGO Power number entities."""
    hub = entry.runtime_data
    async_add_entities([LegoPowerSpeedNumber(hub), LegoPowerPortNumber(hub)])


class LegoPowerSpeedNumber(LegoPowerEntity, RestoreNumber):
    """Live speed control for the motor (percentage of full power).

    Running the motor at full speed can make the LEGO Piano (21323) gears
    skip, so the default is a conservative 50 %.
    """

    _attr_translation_key = "speed"
    _attr_icon = "mdi:speedometer"
    _attr_native_min_value = MIN_SPEED
    _attr_native_max_value = MAX_SPEED
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER

    def __init__(self, hub) -> None:
        """Initialise the speed control."""
        super().__init__(hub)
        self._attr_unique_id = f"{hub.address}_speed"

    @property
    def native_value(self) -> float:
        """Return the current run speed percentage."""
        return float(self._hub.speed)

    async def async_added_to_hass(self) -> None:
        """Restore the last speed set by the user, if any."""
        await super().async_added_to_hass()
        last = await self.async_get_last_number_data()
        if last is not None and last.native_value is not None:
            self._hub.set_speed_value(int(last.native_value))

    async def async_set_native_value(self, value: float) -> None:
        """Update the run speed (applied live if the motor is running)."""
        await self._hub.async_set_speed(int(value))
        self.async_write_ha_state()


class LegoPowerPortNumber(LegoPowerEntity, RestoreNumber):
    """Selects which hub port the motor is plugged into (A=0, B=1, C=2, D=3)."""

    _attr_translation_key = "port"
    _attr_icon = "mdi:usb-port"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = MIN_PORT
    _attr_native_max_value = MAX_PORT
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX

    def __init__(self, hub) -> None:
        """Initialise the port control."""
        super().__init__(hub)
        self._attr_unique_id = f"{hub.address}_port"

    @property
    def native_value(self) -> float:
        """Return the current motor port number."""
        return float(self._hub.port)

    async def async_added_to_hass(self) -> None:
        """Restore the last port set by the user, if any."""
        await super().async_added_to_hass()
        last = await self.async_get_last_number_data()
        if last is not None and last.native_value is not None:
            self._hub.set_port_value(int(last.native_value))

    async def async_set_native_value(self, value: float) -> None:
        """Update the motor port."""
        await self._hub.async_set_port(int(value))
        self.async_write_ha_state()
