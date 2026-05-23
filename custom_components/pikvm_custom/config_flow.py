"""Config flow for PiKVM Custom Controls integration."""
from __future__ import annotations
import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .client import PiKVMClient, PiKVMAuthError, PiKVMConnectionError
from .const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_VERIFY_SSL, DEFAULT_USERNAME, DEFAULT_VERIFY_SSL, DOMAIN

_LOGGER = logging.getLogger(__name__)

class PiKVMFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PiKVM Custom Controls."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Prevent duplicate entries for the same host
            host = user_input[CONF_HOST]
            self._async_abort_entries_match({CONF_HOST: host})

            try:
                client = PiKVMClient(
                    host=host,
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    verify_ssl=user_input.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
                )
                await client.check_connection()
            except PiKVMAuthError:
                errors["base"] = "invalid_auth"
            except PiKVMConnectionError:
                errors["base"] = "cannot_connect"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception: %s", err)
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"PiKVM ({host})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
                }
            ),
            errors=errors,
        )
