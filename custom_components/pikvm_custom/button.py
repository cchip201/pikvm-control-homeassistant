"""Support for PiKVM button controls."""
from __future__ import annotations
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import PiKVMClient
from .const import CONF_HOST, DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the PiKVM button platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    client: PiKVMClient = data["client"]
    host: str = entry.data[CONF_HOST]

    buttons = [
        PiKVMClickButton(client, entry, host, "power", "Power Click", "mdi:power"),
        PiKVMClickButton(client, entry, host, "reset", "Reset Click", "mdi:restart"),
        PiKVMPowerActionButton(client, entry, host, "off_hard", "Power Long Press (Hard Off)", "mdi:power-cycle"),
        PiKVMSystemRebootButton(client, entry, host, "Reboot PiKVM", "mdi:restart-alert"),
    ]

    async_add_entities(buttons)

class PiKVMButtonBase(ButtonEntity):
    """Base class for PiKVM button entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        client: PiKVMClient,
        entry: ConfigEntry,
        host: str,
        name: str,
        icon: str,
    ) -> None:
        """Initialize button."""
        self._client = client
        self._entry = entry
        self._host = host
        self._attr_name = name
        self._attr_icon = icon

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_{self._attr_name.lower().replace(' ', '_')}"

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

class PiKVMClickButton(PiKVMButtonBase):
    """Button to simulate button clicks (power or reset)."""

    def __init__(
        self,
        client: PiKVMClient,
        entry: ConfigEntry,
        host: str,
        button_type: str,
        name: str,
        icon: str,
    ) -> None:
        """Initialize click button."""
        super().__init__(client, entry, host, name, icon)
        self._button_type = button_type

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.debug("Triggering click for button: %s", self._button_type)
        await self._client.click_button(self._button_type)

class PiKVMPowerActionButton(PiKVMButtonBase):
    """Button to invoke specific ATX power state actions (e.g. off_hard)."""

    def __init__(
        self,
        client: PiKVMClient,
        entry: ConfigEntry,
        host: str,
        action: str,
        name: str,
        icon: str,
    ) -> None:
        """Initialize power action button."""
        super().__init__(client, entry, host, name, icon)
        self._action = action

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.debug("Triggering power action: %s", self._action)
        await self._client.set_power_action(self._action)

class PiKVMSystemRebootButton(PiKVMButtonBase):
    """Button to reboot the PiKVM system itself."""

    def __init__(
        self,
        client: PiKVMClient,
        entry: ConfigEntry,
        host: str,
        name: str,
        icon: str,
    ) -> None:
        """Initialize reboot button."""
        super().__init__(client, entry, host, name, icon)

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.debug("Triggering PiKVM system reboot")
        await self._client.reboot_system()

