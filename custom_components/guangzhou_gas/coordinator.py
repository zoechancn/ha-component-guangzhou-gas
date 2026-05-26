"""Data update coordinator for Guangzhou Gas."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    ConfigEntryAuthFailed,
    UpdateFailed,
)

from .api import GuangzhouGasAPI
from .const import DEFAULT_SCAN_INTERVAL
from .exceptions import (
    GuangzhouGasAuthError,
    GuangzhouGasConnectionError,
    GuangzhouGasAPIError,
)

_LOGGER = logging.getLogger(__name__)


class GuangzhouGasDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Guangzhou Gas data."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        api: GuangzhouGasAPI,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator.
        
        Args:
            hass: Home Assistant instance.
            api: Guangzhou Gas API client.
            scan_interval: Update interval in seconds.
        """
        super().__init__(
            hass,
            _LOGGER,
            name="guangzhou_gas",
            update_interval=timedelta(seconds=scan_interval),
        )
        self._api = api
        self._scan_interval = scan_interval
        
    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via API.
        
        Returns:
            Merged user info and gas detail data.
            
        Raises:
            ConfigEntryAuthFailed: Authentication failed.
            UpdateFailed: Update failed.
        """
        _LOGGER.debug("Starting data update")
        
        try:
            # 每次更新都重新登录获取新 token
            _LOGGER.debug("Logging in...")
            token = await self._api.async_login()
            
            # 获取用户信息
            _LOGGER.debug("Getting user info...")
            user_info = await self._api.async_get_user_info(token)
            _LOGGER.debug("User info received: %s", user_info)
            
            # 从用户信息中获取 user_no，用于查询燃气详情
            user_no = user_info.get("userNo", "")
            if not user_no:
                _LOGGER.error("userNo not found in user_info")
                raise UpdateFailed("userNo not found in user info")
            
            # 获取燃气详情
            _LOGGER.debug("Getting gas detail for user %s...", user_no)
            gas_detail = await self._api.async_get_gas_detail(token, user_no)
            _LOGGER.debug("Gas detail received: %s", gas_detail)
            
            # 合并数据（扁平结构）
            data = {
                **user_info,
                **gas_detail,
            }
            
            _LOGGER.debug("Data update successful: %s", data)
            return data
            
        except GuangzhouGasAuthError as err:
            _LOGGER.error("Authentication failed, please reconfigure: %s", err)
            raise ConfigEntryAuthFailed from err
            
        except GuangzhouGasConnectionError as err:
            _LOGGER.warning("Connection failed, will retry: %s", err)
            raise UpdateFailed(f"Connection failed: {err}") from err
            
        except GuangzhouGasAPIError as err:
            _LOGGER.error("API error: %s", err)
            raise UpdateFailed(f"API error: {err}") from err
            
        except Exception as err:
            _LOGGER.exception("Unexpected error during data update")
            raise UpdateFailed(f"Unexpected error: {err}") from err
