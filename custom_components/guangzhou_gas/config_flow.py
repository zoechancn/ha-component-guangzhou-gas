"""Config flow for Guangzhou Gas."""

from __future__ import annotations

import logging
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import GuangzhouGasAPI
from .const import (
    CONF_ACCEPT_KEY,
    CONF_NICKNAME,
    CONF_SCAN_INTERVAL,
    CONF_UNIONID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)
from .exceptions import (
    GuangzhouGasAPIError,
    GuangzhouGasAuthError,
    GuangzhouGasConnectionError,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NICKNAME): cv.string,
        vol.Required(CONF_ACCEPT_KEY): cv.string,
        vol.Required(CONF_UNIONID): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            cv.positive_int,
            vol.Range(min=MIN_SCAN_INTERVAL),
        ),
    }
)


class GuangzhouGasConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Guangzhou Gas."""

    VERSION = 1
    MINOR_VERSION = 0

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_name, error = await self._test_connection(user_input)
            if user_name is not None:
                return self.async_create_entry(
                    title=f"广州燃气 - {user_name}",
                    data=user_input,
                )
            errors["base"] = error

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle reconfiguration."""
        errors: dict[str, str] = {}
        config_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        if config_entry is None:
            return self.async_abort(reason="unknown")

        if user_input is not None:
            user_name, error = await self._test_connection(user_input)
            if user_name is not None:
                self.hass.config_entries.async_update_entry(
                    config_entry,
                    title=f"广州燃气 - {user_name}",
                    data=user_input,
                )
                return self.async_abort(reason="reconfigure_success")
            errors["base"] = error

        schema = self.add_suggested_values_to_schema(
            STEP_USER_DATA_SCHEMA,
            config_entry.data,
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema,
            errors=errors,
        )

    async def _test_connection(
        self, user_input: dict[str, Any]
    ) -> tuple[str | None, str]:
        """Validate credentials and return the account display name."""
        try:
            session = async_get_clientsession(self.hass)
            api = GuangzhouGasAPI(
                session,
                user_input[CONF_NICKNAME],
                user_input[CONF_ACCEPT_KEY],
                user_input[CONF_UNIONID],
            )

            token = await api.async_login()
            user_info = await api.async_get_user_info(token)
            user_name = user_info.get("userName")

            if not user_name:
                _LOGGER.warning("Guangzhou Gas response did not include a user name")
                return None, "cannot_get_user_info"

            return str(user_name), ""

        except GuangzhouGasAuthError:
            return None, "auth_failed"

        except GuangzhouGasConnectionError:
            return None, "connection_failed"

        except GuangzhouGasAPIError:
            return None, "api_error"

        except Exception:
            _LOGGER.exception(
                "Unexpected error while validating Guangzhou Gas credentials"
            )
            return None, "unknown_error"
