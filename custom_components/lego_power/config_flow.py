"""Config flow for the LEGO Power integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_DIRECTION,
    CONF_POWER,
    CONF_PORT,
    CONF_STOP_ACTION,
    DEFAULT_DIRECTION,
    DEFAULT_POWER,
    DEFAULT_PORT,
    DEFAULT_STOP_ACTION,
    DIRECTION_FORWARD,
    DIRECTION_REVERSE,
    DOMAIN,
    LEGO_HUB_SERVICE_UUID,
    LEGO_MANUFACTURER_ID,
    MAX_PORT,
    MAX_POWER,
    MIN_PORT,
    MIN_POWER,
    STOP_BRAKE,
    STOP_FLOAT,
)

_DIRECTION_SELECTOR = selector.SelectSelector(
    selector.SelectSelectorConfig(
        options=[DIRECTION_FORWARD, DIRECTION_REVERSE],
        translation_key="direction",
        mode=selector.SelectSelectorMode.DROPDOWN,
    )
)
_STOP_SELECTOR = selector.SelectSelector(
    selector.SelectSelectorConfig(
        options=[STOP_FLOAT, STOP_BRAKE],
        translation_key="stop_action",
        mode=selector.SelectSelectorMode.DROPDOWN,
    )
)
_PORT_SELECTOR = selector.NumberSelector(
    selector.NumberSelectorConfig(
        min=MIN_PORT, max=MAX_PORT, step=1, mode=selector.NumberSelectorMode.BOX
    )
)
_POWER_SELECTOR = selector.NumberSelector(
    selector.NumberSelectorConfig(
        min=MIN_POWER,
        max=MAX_POWER,
        step=1,
        mode=selector.NumberSelectorMode.SLIDER,
        unit_of_measurement="%",
    )
)


def _is_lego_hub(info: BluetoothServiceInfoBleak) -> bool:
    """Return True if the advertisement looks like a LEGO Powered Up hub."""
    if LEGO_HUB_SERVICE_UUID in info.service_uuids:
        return True
    return LEGO_MANUFACTURER_ID in info.manufacturer_data


def _settings_schema(defaults: dict[str, Any]) -> vol.Schema:
    """Build the per-device settings schema."""
    return vol.Schema(
        {
            vol.Required(CONF_PORT, default=defaults[CONF_PORT]): _PORT_SELECTOR,
            vol.Required(CONF_POWER, default=defaults[CONF_POWER]): _POWER_SELECTOR,
            vol.Required(
                CONF_DIRECTION, default=defaults[CONF_DIRECTION]
            ): _DIRECTION_SELECTOR,
            vol.Required(
                CONF_STOP_ACTION, default=defaults[CONF_STOP_ACTION]
            ): _STOP_SELECTOR,
        }
    )


class LegoPowerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the LEGO Power config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialise the flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle a hub discovered over Bluetooth."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {
            "name": discovery_info.name or discovery_info.address
        }
        return await self.async_step_settings()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow started by the user; let them pick a hub."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            self._discovery_info = self._discovered.get(address)
            return await self.async_step_settings()

        current_addresses = self._async_current_ids()
        devices: dict[str, str] = {}
        for info in async_discovered_service_info(self.hass, connectable=True):
            if info.address in current_addresses or not _is_lego_hub(info):
                continue
            self._discovered[info.address] = info
            devices[info.address] = f"{info.name or 'LEGO hub'} ({info.address})"

        if not devices:
            return self.async_abort(reason="no_devices_found")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): vol.In(devices)}),
        )

    async def async_step_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Collect the per-device name and motor settings."""
        if user_input is not None:
            address = self.unique_id
            assert address is not None
            name = user_input[CONF_NAME]
            return self.async_create_entry(
                title=name,
                data={CONF_ADDRESS: address},
                options={
                    CONF_PORT: int(user_input[CONF_PORT]),
                    CONF_POWER: int(user_input[CONF_POWER]),
                    CONF_DIRECTION: user_input[CONF_DIRECTION],
                    CONF_STOP_ACTION: user_input[CONF_STOP_ACTION],
                },
            )

        default_name = "LEGO Power"
        if self._discovery_info and self._discovery_info.name:
            default_name = self._discovery_info.name

        schema = vol.Schema(
            {vol.Required(CONF_NAME, default=default_name): str}
        ).extend(
            _settings_schema(
                {
                    CONF_PORT: DEFAULT_PORT,
                    CONF_POWER: DEFAULT_POWER,
                    CONF_DIRECTION: DEFAULT_DIRECTION,
                    CONF_STOP_ACTION: DEFAULT_STOP_ACTION,
                }
            ).schema
        )

        return self.async_show_form(
            step_id="settings",
            data_schema=schema,
            description_placeholders={"name": default_name},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> OptionsFlow:
        """Return the options flow."""
        return LegoPowerOptionsFlow()


class LegoPowerOptionsFlow(OptionsFlow):
    """Handle changing motor settings after setup."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}
        defaults = {
            CONF_PORT: current.get(CONF_PORT, DEFAULT_PORT),
            CONF_POWER: current.get(CONF_POWER, DEFAULT_POWER),
            CONF_DIRECTION: current.get(CONF_DIRECTION, DEFAULT_DIRECTION),
            CONF_STOP_ACTION: current.get(CONF_STOP_ACTION, DEFAULT_STOP_ACTION),
        }
        return self.async_show_form(
            step_id="init", data_schema=_settings_schema(defaults)
        )
