"""PiKVM API Client."""
import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)

class PiKVMClientError(Exception):
    """Base exception for PiKVM Client errors."""

class PiKVMAuthError(PiKVMClientError):
    """Authentication failed."""

class PiKVMConnectionError(PiKVMClientError):
    """Connection to host failed."""

class PiKVMClient:
    """Async API Client for PiKVM."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        verify_ssl: bool = False,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize client."""
        self._host = host.rstrip("/")
        if not self._host.startswith(("http://", "https://")):
            self._host = f"https://{self._host}"
        self._username = username
        self._password = password
        self._verify_ssl = verify_ssl
        self._session = session or aiohttp.ClientSession()
        self._auth = aiohttp.BasicAuth(username, password)

    async def check_connection(self) -> bool:
        """Validate connection credentials and state endpoint."""
        try:
            await self.get_atx_state()
            return True
        except PiKVMAuthError:
            raise
        except Exception as err:
            raise PiKVMConnectionError(f"Connection failed to {self._host}: {err}") from err

    async def get_atx_state(self) -> dict:
        """Fetch current ATX status from /api/atx."""
        url = f"{self._host}/api/atx"
        try:
            async with self._session.get(
                url,
                auth=self._auth,
                ssl=self._verify_ssl,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                if response.status in (401, 403):
                    raise PiKVMAuthError("Invalid credentials provided.")
                response.raise_for_status()
                data = await response.json()
                _LOGGER.debug("PiKVM state payload: %s", data)
                return data.get("result", {})
        except aiohttp.ClientError as err:
            raise PiKVMConnectionError(f"Network error getting state: {err}") from err

    async def click_button(self, button: str) -> bool:
        """Simulate ATX physical button press (e.g. power, reset)."""
        url = f"{self._host}/api/atx/click"
        params = {"button": button}
        try:
            async with self._session.post(
                url,
                auth=self._auth,
                params=params,
                ssl=self._verify_ssl,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                if response.status in (401, 403):
                    raise PiKVMAuthError("Invalid credentials.")
                response.raise_for_status()
                data = await response.json()
                return data.get("ok", False)
        except aiohttp.ClientError as err:
            raise PiKVMConnectionError(f"Network error pressing {button} button: {err}") from err

    async def set_power_action(self, action: str) -> bool:
        """Set ATX power action (e.g. off_hard, on, off, reset_hard)."""
        url = f"{self._host}/api/atx/power"
        params = {"action": action}
        try:
            async with self._session.post(
                url,
                auth=self._auth,
                params=params,
                ssl=self._verify_ssl,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                if response.status in (401, 403):
                    raise PiKVMAuthError("Invalid credentials.")
                response.raise_for_status()
                data = await response.json()
                return data.get("ok", False)
        except aiohttp.ClientError as err:
            raise PiKVMConnectionError(f"Network error calling power action {action}: {err}") from err
