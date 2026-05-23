"""Support for PiKVM sensors."""
from __future__ import annotations
from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import CONF_HOST, DOMAIN
from .coordinator import PiKVMDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the PiKVM sensor platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PiKVMDataUpdateCoordinator = data["coordinator"]
    host: str = entry.data[CONF_HOST]

    sensors = [
        # CPU Temperature
        PiKVMSensor(
            coordinator, entry, host, "CPU Temperature", "cpu_temp",
            ["info", "hw", "temp", "cpu"], SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS
        ),
        # Fan Speed
        PiKVMSensor(
            coordinator, entry, host, "Fan Speed", "fan_speed",
            ["info", "fan", "speed"], None,
            SensorStateClass.MEASUREMENT, "RPM", "mdi:fan"
        ),
        # System Uptime (calculated as boot timestamp)
        PiKVMTimestampSensor(
            coordinator, entry, host, "Boot Time", "boot_time",
            ["info", "system", "uptime"], SensorDeviceClass.TIMESTAMP
        ),
        # KVMD Version
        PiKVMSensor(
            coordinator, entry, host, "KVMD Version", "kvmd_version",
            ["info", "system", "kvmd", "version"], None,
            None, None, "mdi:information-outline"
        ),
    ]

    async_add_entities(sensors)

class PiKVMSensor(CoordinatorEntity[PiKVMDataUpdateCoordinator], SensorEntity):
    """Representation of a generic PiKVM sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PiKVMDataUpdateCoordinator,
        entry: ConfigEntry,
        host: str,
        name: str,
        unique_id_suffix: str,
        data_path: list[str],
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        native_unit_of_measurement: str | None = None,
        icon: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._host = host
        self._attr_name = name
        self._unique_id_suffix = unique_id_suffix
        self._data_path = data_path
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = native_unit_of_measurement
        self._attr_icon = icon

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_{self._unique_id_suffix}"

    @property
    def native_value(self) -> str | int | float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        val = self.coordinator.data
        for key in self._data_path:
            if not isinstance(val, dict):
                return None
            val = val.get(key)
        return val

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

class PiKVMTimestampSensor(PiKVMSensor):
    """Representation of a PiKVM timestamp sensor (calculates boot time dynamically)."""

    @property
    def native_value(self) -> str | None:
        """Return boot timestamp value."""
        uptime_seconds = super().native_value
        if uptime_seconds is None or not isinstance(uptime_seconds, (int, float)):
            return None
        
        # Calculate boot time relative to current UTC time
        boot_time = dt_util.utcnow() - timedelta(seconds=uptime_seconds)
        return boot_time
