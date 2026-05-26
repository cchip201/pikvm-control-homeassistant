"""Support for PiKVM switches."""
from __future__ import annotations
import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .client import PiKVMClient
from .const import CONF_HOST, DOMAIN
from .coordinator import PiKVMDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the PiKVM switch platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PiKVMDataUpdateCoordinator = data["coordinator"]
    client: PiKVMClient = data["client"]
    host: str = entry.data[CONF_HOST]

    switches = [
        PiKVMPowerSwitch(coordinator, client, entry, host, "ATX Power", "atx_power"),
        PiKVMMsdSwitch(coordinator, client, entry, host, "Virtual Media", "virtual_media"),
    ]
    async_add_entities(switches)

class PiKVMBaseSwitch(CoordinatorEntity[PiKVMDataUpdateCoordinator], SwitchEntity):
    """Base class for PiKVM switch entities."""
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PiKVMDataUpdateCoordinator,
        client: PiKVMClient,
        entry: ConfigEntry,
        host: str,
        name: str,
        unique_id_suffix: str,
    ) -> None:
        """Initialize switch."""
        super().__init__(coordinator)
        self._client = client
        self._entry = entry
        self._host = host
        self._attr_name = name
        self._unique_id_suffix = unique_id_suffix

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_{self._unique_id_suffix}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device details."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"PiKVM ({self._host})",
            manufacturer="PiKVM",
            model="PiKVM V3/V4",
            configuration_url=f"https://{self._host}",
        )

class PiKVMPowerSwitch(PiKVMBaseSwitch):
    """ATX Power switch."""
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_icon = "mdi:power"

    @property
    def is_on(self) -> bool | None:
        """Return true if power is on."""
        if not self.coordinator.data:
            return None
        val = self.coordinator.data.get("atx", {}).get("leds", {}).get("power")
        return bool(val)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on."""
        await self._client.set_power_action("on")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""
        await self._client.set_power_action("off_hard")
        await self.coordinator.async_request_refresh()


class PiKVMMsdSwitch(PiKVMBaseSwitch):
    """Virtual Media (MSD) Switch."""
    _attr_icon = "mdi:usb-flash-drive"

    @property
    def is_on(self) -> bool | None:
        """Return true if Virtual Media is connected."""
        if not self.coordinator.data:
            return None
        info = self.coordinator.data.get("info", {})
        extras = info.get("extras")
        if isinstance(extras, dict):
            msd_service = extras.get("msd")
            if isinstance(msd_service, dict):
                return bool(msd_service.get("started"))
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on."""
        await self._client.set_msd_state(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""
        await self._client.set_msd_state(False)
        await self.coordinator.async_request_refresh()
