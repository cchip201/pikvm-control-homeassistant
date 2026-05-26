"""Support for PiKVM selects."""
from __future__ import annotations
import logging

from homeassistant.components.select import SelectEntity
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
    """Set up the PiKVM select platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PiKVMDataUpdateCoordinator = data["coordinator"]
    client: PiKVMClient = data["client"]
    host: str = entry.data[CONF_HOST]

    selects = [
        PiKVMUsbModeSelect(coordinator, client, entry, host, "USB HID Mode", "usb_hid_mode"),
    ]
    async_add_entities(selects)

class PiKVMBaseSelect(CoordinatorEntity[PiKVMDataUpdateCoordinator], SelectEntity):
    """Base class for PiKVM select entities."""
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
        """Initialize select."""
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

class PiKVMUsbModeSelect(PiKVMBaseSelect):
    """USB HID Mode select."""
    _attr_icon = "mdi:usb"
    _attr_options = ["hid", "msd", "hid+msd", "disabled"]

    @property
    def current_option(self) -> str | None:
        """Return current mode."""
        if not self.coordinator.data:
            return None
        info = self.coordinator.data.get("info", {})
        extras = info.get("extras", {})
        if isinstance(extras, dict):
            hid_mode = extras.get("hid", {}).get("mode")
            if hid_mode in self._attr_options:
                return hid_mode
        return "hid" # Default fallback

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self._client.set_usb_mode(option)
        await self.coordinator.async_request_refresh()
