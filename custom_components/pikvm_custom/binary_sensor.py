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
        # Physical LEDs from ATX State
        PiKVMBinarySensor(
            coordinator, entry, host, "Power LED", "power_led",
            ["atx", "leds", "power"], BinarySensorDeviceClass.POWER
        ),
        PiKVMBinarySensor(
            coordinator, entry, host, "HDD LED", "hdd_led",
            ["atx", "leds", "hdd"], BinarySensorDeviceClass.RUNNING
        ),
        # Hardware Throttling State
        PiKVMBinarySensor(
            coordinator, entry, host, "Throttling Alert", "throttled",
            ["info", "hw", "throttled"], BinarySensorDeviceClass.PROBLEM
        ),
        # Services Statuses
        PiKVMBinarySensor(
            coordinator, entry, host, "IPMI Service", "service_ipmi",
            ["info", "system", "services", "ipmi", "active"],
            BinarySensorDeviceClass.RUNNING, "mdi:server"
        ),
        PiKVMBinarySensor(
            coordinator, entry, host, "Janus WebRTC Service", "service_janus",
            ["info", "system", "services", "janus", "active"],
            BinarySensorDeviceClass.RUNNING, "mdi:webrtc"
        ),
        PiKVMBinarySensor(
            coordinator, entry, host, "VNC Service", "service_vnc",
            ["info", "system", "services", "vnc", "active"],
            BinarySensorDeviceClass.RUNNING, "mdi:screencast"
        ),
        PiKVMBinarySensor(
            coordinator, entry, host, "Webterm Service", "service_webterm",
            ["info", "system", "services", "webterm", "active"],
            BinarySensorDeviceClass.RUNNING, "mdi:console-line"
        ),
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
        name: str,
        unique_id_suffix: str,
        data_path: list[str],
        device_class: BinarySensorDeviceClass | None = None,
        icon: str | None = None,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._host = host
        self._attr_name = name
        self._unique_id_suffix = unique_id_suffix
        self._data_path = data_path
        self._attr_device_class = device_class
        self._attr_icon = icon

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_{self._unique_id_suffix}"

    @property
    def is_on(self) -> bool | None:
        """Return true if binary sensor is on."""
        if not self.coordinator.data:
            return None
        
        # Resolve nested properties dynamically
        val = self.coordinator.data
        for key in self._data_path:
            if not isinstance(val, dict):
                return None
            val = val.get(key)
        return bool(val)

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
