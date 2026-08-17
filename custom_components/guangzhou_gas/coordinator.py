"""Data coordinator for Guangzhou Gas."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    ConfigEntryAuthFailed,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import GuangzhouGasAPI
from .exceptions import (
    GuangzhouGasAPIError,
    GuangzhouGasAuthError,
    GuangzhouGasConnectionError,
)

_LOGGER = logging.getLogger(__name__)


class GuangzhouGasDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch and share one Guangzhou Gas account snapshot."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: GuangzhouGasAPI,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger=_LOGGER,
            name="广州燃气",
            update_interval=timedelta(seconds=scan_interval),
        )
        self._api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Log in, fetch account and meter data, and merge the result."""
        try:
            token = await self._api.async_login()
            user_info = await self._api.async_get_user_info(token)
            user_no = str(user_info.get("userNo") or "")
            if not user_no:
                raise UpdateFailed("The account response did not contain a user number")
            meter_detail = await self._api.async_get_gas_detail(token, user_no)
            return {**user_info, **meter_detail}
        except GuangzhouGasAuthError as err:
            raise ConfigEntryAuthFailed(
                "Guangzhou Gas credentials are no longer valid"
            ) from err
        except (GuangzhouGasConnectionError, GuangzhouGasAPIError) as err:
            raise UpdateFailed(str(err)) from err
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Unexpected Guangzhou Gas response: {err}") from err
