"""Data Update Coordinator for PiKVM."""
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import PiKVMClient, PiKVMClientError

_LOGGER = logging.getLogger(__name__)

class PiKVMDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Class to manage fetching PiKVM data from the API."""

    def __init__(self, hass: HomeAssistant, client: PiKVMClient) -> None:
        """Initialize coordinator."""
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name="pikvm_custom",
            update_interval=timedelta(seconds=5),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from PiKVM."""
        try:
            atx_state = await self.client.get_atx_state()
            system_info = await self.client.get_system_info()
            return {
                "atx": atx_state,
                "info": system_info,
            }
        except PiKVMClientError as err:
            raise UpdateFailed(f"Error communicating with PiKVM: {err}") from err
