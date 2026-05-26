"""Config flow for Guangzhou Gas."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigFlow, OptionsFlow
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_NICKNAME,
    CONF_ACCEPT_KEY,
    CONF_UNIONID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)
from .api import GuangzhouGasAPI
from .exceptions import (
    GuangzhouGasAuthError,
    GuangzhouGasConnectionError,
    GuangzhouGasAPIError,
)

_LOGGER = logging.getLogger(__name__)

# 配置 Schema
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NICKNAME): cv.string,
        vol.Required(CONF_ACCEPT_KEY): cv.string,
        vol.Required(CONF_UNIONID): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
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
        """Handle the initial step.
        
        Args:
            user_input: User input dictionary.
            
        Returns:
            FlowResult.
        """
        errors = {}
        
        if user_input is not None:
            # 验证用户输入
            is_valid, error_msg = await self._test_connection(user_input)
            
            if is_valid:
                # 创建配置条目
                return self.async_create_entry(
                    title=f"广州燃气 - {error_msg}",  # error_msg 包含用户名
                    data=user_input,
                )
            else:
                errors["base"] = error_msg
                
        # 显示配置表单
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
        
    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle reconfiguration.
        
        Args:
            user_input: User input dictionary.
            
        Returns:
            FlowResult.
        """
        errors = {}
        config_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        
        if user_input is not None:
            # 验证用户输入
            is_valid, error_msg = await self._test_connection(user_input)
            
            if is_valid:
                # 更新配置条目
                self.hass.config_entries.async_update_entry(
                    config_entry,
                    data=user_input,
                )
                return self.async_abort(reason="reconfigure_success")
            else:
                errors["base"] = error_msg
                
        # 使用当前配置作为默认值
        schema = self.add_suggested_values_to_schema(
            STEP_USER_DATA_SCHEMA,
            config_entry.data,
        )
        
        # 显示配置表单
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema,
            errors=errors,
        )
        
    async def _test_connection(self, user_input: dict[str, Any]) -> tuple[bool, str]:
        """Test API connection.
        
        Args:
            user_input: User input dictionary.
            
        Returns:
            Tuple of (is_valid, message).
        """
        try:
            session = async_get_clientsession(self.hass)
            api = GuangzhouGasAPI(
                session,
                user_input[CONF_NICKNAME],
                user_input[CONF_ACCEPT_KEY],
                user_input[CONF_UNIONID],
            )
            
            # 测试登录
            token = await api.async_login()
            _LOGGER.info("Login successful")
            
            # 测试获取用户信息
            user_info = await api.async_get_user_info(token)
            user_name = user_info.get("data", {}).get("userName")
            
            if not user_name:
                _LOGGER.warning("User name not found in response")
                return False, "cannot_get_user_info"
                
            _LOGGER.info("Connection test successful, user: %s", user_name)
            return True, user_name
            
        except GuangzhouGasAuthError:
            _LOGGER.error("Authentication failed")
            return False, "auth_failed"
            
        except GuangzhouGasConnectionError:
            _LOGGER.error("Connection failed")
            return False, "connection_failed"
            
        except GuangzhouGasAPIError as err:
            _LOGGER.error("API error: %s", err)
            return False, "api_error"
            
        except Exception as err:
            _LOGGER.exception("Unexpected error: %s", err)
            return False, "unknown_error"
