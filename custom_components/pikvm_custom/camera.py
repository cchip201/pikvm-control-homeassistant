"""Camera platform for PiKVM Custom Controls."""
from homeassistant.components.camera import HTTP_BASIC_AUTHENTICATION
from homeassistant.components.mjpeg.camera import MjpegCamera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_HOST, CONF_USERNAME, CONF_PASSWORD

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the PiKVM camera from a config entry."""
    host = entry.data[CONF_HOST]
    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    
    mjpeg_url = f"http://{host}:8080/stream"
    still_image_url = f"http://{host}:8080/snapshot"

    async_add_entities([PiKVMCamera(entry, mjpeg_url, still_image_url, username, password)])


class PiKVMCamera(MjpegCamera):
    """Representation of a PiKVM MJPEG stream."""

    def __init__(
        self, 
        entry: ConfigEntry, 
        mjpeg_url: str, 
        still_image_url: str,
        username: str | None,
        password: str | None,
    ) -> None:
        """Initialize the camera."""
        super().__init__(
            name="PiKVM Video Stream",
            mjpeg_url=mjpeg_url,
            still_image_url=still_image_url,
            username=username,
            password=password,
            authentication=HTTP_BASIC_AUTHENTICATION,
        )
        self._attr_unique_id = f"{entry.entry_id}_camera"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"PiKVM ({entry.data[CONF_HOST]})",
            manufacturer="PiKVM",
        )
