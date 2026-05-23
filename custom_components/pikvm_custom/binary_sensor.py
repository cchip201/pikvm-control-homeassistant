"""Support for PiKVM binary sensors."""
from __future__ import annotations
import logging

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_HOST, DOMAIN
from .coordinator import PiKVMDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the PiKVM binary sensor platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PiKVMDataUpdateCoordinator = data["coordinator"]
    host: str = entry.data[CONF_HOST]

    sensors = [
        PiKVMBinarySensor(coordinator, entry, host, "power", "Power LED", BinarySensorDeviceClass.POWER),
        PiKVMBinarySensor(coordinator, entry, host, "hdd", "HDD LED", BinarySensorDeviceClass.RUNNING),
    ]

    async_add_entities(sensors)

class PiKVMBinarySensor(CoordinatorEntity[PiKVMDataUpdateCoordinator], BinarySensorEntity):
    """Representation of a PiKVM state binary sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PiKVMDataUpdateCoordinator,
        entry: ConfigEntry,
        host: str,
        led_key: str,
        name: str,
        device_class: BinarySensorDeviceClass | None = None,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._host = host
        self._led_key = led_key
        self._attr_name = name
        self._attr_device_class = device_class

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_{self._led_key}_led"

    @property
    def is_on(self) -> bool | None:
        """Return true if binary sensor is on."""
        if not self.coordinator.data:
            return None
        leds = self.coordinator.data.get("leds", {})
        return bool(leds.get(self._led_key, False))

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
