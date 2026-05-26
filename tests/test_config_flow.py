"""Tests for Guangzhou Gas config flow."""
from __future__ import annotations

import pytest
from typing import Any, Dict, Tuple
from unittest.mock import AsyncMock, patch, MagicMock

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigFlow, ConfigEntry
from homeassistant.data_entry_flow import FlowResult

from custom_components.guangzhou_gas.config_flow import GuangzhouGasConfigFlow
from custom_components.guangzhou_gas.const import (
    DOMAIN,
    CONF_NICKNAME,
    CONF_ACCEPT_KEY,
    CONF_UNIONID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)
from custom_components.guangzhou_gas.exceptions import (
    GuangzhouGasAuthError,
    GuangzhouGasConnectionError,
    GuangzhouGasAPIError,
)


# 模拟配置输入
VALID_CONFIG = {
    CONF_NICKNAME: "test_user",
    CONF_ACCEPT_KEY: "test_accept_key_12345",
    CONF_UNIONID: "test_unionid_67890",
    CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
}

INVALID_CONFIG = {
    CONF_NICKNAME: "",
    CONF_ACCEPT_KEY: "",
    CONF_UNIONID: "",
}


class MockConfigFlow(GuangzhouGasConfigFlow):
    """Mock config flow for testing."""
    
    def __init__(self):
        """Initialize mock config flow."""
        super().__init__()
        self.hass = MagicMock(spec=HomeAssistant)
        self.context = {"entry_id": "test_entry_id"}
        self._async_show_form_calls = []
        self._async_create_entry_calls = []
        self._async_abort_calls = []
    
    def async_show_form(self, **kwargs) -> FlowResult:
        """Mock async_show_form."""
        self._async_show_form_calls.append(kwargs)
        return {"type": "form", **kwargs}
    
    def async_create_entry(self, **kwargs) -> FlowResult:
        """Mock async_create_entry."""
        self._async_create_entry_calls.append(kwargs)
        return {"type": "create_entry", **kwargs}
    
    def async_abort(self, **kwargs) -> FlowResult:
        """Mock async_abort."""
        self._async_abort_calls.append(kwargs)
        return {"type": "abort", **kwargs}
    
    def add_suggested_values_to_schema(self, schema, suggested_values):
        """Mock add_suggested_values_to_schema."""
        return schema


@pytest.fixture
def config_flow() -> MockConfigFlow:
    """Create a mock config flow."""
    return MockConfigFlow()


class TestGuangzhouGasConfigFlow:
    """Test GuangzhouGasConfigFlow."""
    
    # ==================== async_step_user 测试 ====================
    
    @pytest.mark.asyncio
    async def test_step_user_show_form(self, config_flow: MockConfigFlow):
        """Test step_user shows form when no user input."""
        result = await config_flow.async_step_user(user_input=None)
        
        assert result["type"] == "form"
        assert result["step_id"] == "user"
        assert len(config_flow._async_show_form_calls) == 1
    
    @pytest.mark.asyncio
    async def test_step_user_valid_config(self, config_flow: MockConfigFlow):
        """Test step_user with valid config."""
        # Mock _test_connection to return success
        config_flow._test_connection = AsyncMock(return_value=(True, "测试用户"))
        
        result = await config_flow.async_step_user(user_input=VALID_CONFIG.copy())
        
        assert result["type"] == "create_entry"
        assert "测试用户" in result["title"]
        assert result["data"] == VALID_CONFIG
    
    @pytest.mark.asyncio
    async def test_step_user_invalid_config(self, config_flow: MockConfigFlow):
        """Test step_user with invalid config (connection fails)."""
        # Mock _test_connection to return failure
        config_flow._test_connection = AsyncMock(return_value=(False, "auth_failed"))
        
        result = await config_flow.async_step_user(user_input=VALID_CONFIG.copy())
        
        assert result["type"] == "form"
        assert result["errors"]["base"] == "auth_failed"
    
    # ==================== async_step_reconfigure 测试 ====================
    
    @pytest.mark.asyncio
    async def test_step_reconfigure_show_form(self, config_flow: MockConfigFlow):
        """Test step_reconfigure shows form with current config."""
        # Mock config entry
        config_flow.hass.config_entries.async_get_entry = MagicMock(
            return_value=MagicMock(data=VALID_CONFIG.copy())
        )
        
        result = await config_flow.async_step_reconfigure(user_input=None)
        
        assert result["type"] == "form"
        assert result["step_id"] == "reconfigure"
    
    @pytest.mark.asyncio
    async def test_step_reconfigure_valid_config(self, config_flow: MockConfigFlow):
        """Test step_reconfigure with valid config."""
        # Mock config entry
        mock_entry = MagicMock(data=VALID_CONFIG.copy())
        config_flow.hass.config_entries.async_get_entry = MagicMock(return_value=mock_entry)
        config_flow.hass.config_entries.async_update_entry = MagicMock()
        
        # Mock _test_connection to return success
        config_flow._test_connection = AsyncMock(return_value=(True, "测试用户"))
        
        result = await config_flow.async_step_reconfigure(user_input=VALID_CONFIG.copy())
        
        assert result["type"] == "abort"
        assert result["reason"] == "reconfigure_success"
    
    @pytest.mark.asyncio
    async def test_step_reconfigure_invalid_config(self, config_flow: MockConfigFlow):
        """Test step_reconfigure with invalid config."""
        # Mock config entry
        mock_entry = MagicMock(data=VALID_CONFIG.copy())
        config_flow.hass.config_entries.async_get_entry = MagicMock(return_value=mock_entry)
        
        # Mock _test_connection to return failure
        config_flow._test_connection = AsyncMock(return_value=(False, "connection_failed"))
        
        result = await config_flow.async_step_reconfigure(user_input=VALID_CONFIG.copy())
        
        assert result["type"] == "form"
        assert result["errors"]["base"] == "connection_failed"
    
    # ==================== _test_connection 测试 ====================
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, config_flow: MockConfigFlow):
        """Test _test_connection success."""
        # Mock API
        mock_api = AsyncMock()
        mock_api.async_login = AsyncMock(return_value="test_token")
        mock_api.async_get_user_info = AsyncMock(
            return_value={"data": {"userName": "测试用户"}}
        )
        
        with patch("custom_components.guangzhou_gas.config_flow.GuangzhouGasAPI", return_value=mock_api):
            config_flow.hass.async_get_clientsession = MagicMock(return_value=AsyncMock())
            
            result = await config_flow._test_connection(VALID_CONFIG.copy())
            
            assert result == (True, "测试用户")
    
    @pytest.mark.asyncio
    async def test_test_connection_auth_failed(self, config_flow: MockConfigFlow):
        """Test _test_connection with auth failure."""
        from custom_components.guangzhou_gas.exceptions import GuangzhouGasAuthError
        
        # Mock API to raise auth error
        mock_api = AsyncMock()
        mock_api.async_login = AsyncMock(side_effect=GuangzhouGasAuthError("Authentication failed"))
        
        with patch("custom_components.guangzhou_gas.config_flow.GuangzhouGasAPI", return_value=mock_api):
            config_flow.hass.async_get_clientsession = MagicMock(return_value=AsyncMock())
            
            result = await config_flow._test_connection(VALID_CONFIG.copy())
            
            assert result == (False, "auth_failed")
    
    @pytest.mark.asyncio
    async def test_test_connection_connection_error(self, config_flow: MockConfigFlow):
        """Test _test_connection with connection error."""
        from custom_components.guangzhou_gas.exceptions import GuangzhouGasConnectionError
        
        # Mock API to raise connection error
        mock_api = AsyncMock()
        mock_api.async_login = AsyncMock(side_effect=GuangzhouGasConnectionError("Connection failed"))
        
        with patch("custom_components.guangzhou_gas.config_flow.GuangzhouGasAPI", return_value=mock_api):
            config_flow.hass.async_get_clientsession = MagicMock(return_value=AsyncMock())
            
            result = await config_flow._test_connection(VALID_CONFIG.copy())
            
            assert result == (False, "connection_failed")
    
    @pytest.mark.asyncio
    async def test_test_connection_api_error(self, config_flow: MockConfigFlow):
        """Test _test_connection with API error."""
        from custom_components.guangzhou_gas.exceptions import GuangzhouGasAPIError
        
        # Mock API to raise API error
        mock_api = AsyncMock()
        mock_api.async_login = AsyncMock(side_effect=GuangzhouGasAPIError("API error"))
        
        with patch("custom_components.guangzhou_gas.config_flow.GuangzhouGasAPI", return_value=mock_api):
            config_flow.hass.async_get_clientsession = MagicMock(return_value=AsyncMock())
            
            result = await config_flow._test_connection(VALID_CONFIG.copy())
            
            assert result == (False, "api_error")
    
    @pytest.mark.asyncio
    async def test_test_connection_no_user_name(self, config_flow: MockConfigFlow):
        """Test _test_connection when user name not found."""
        # Mock API
        mock_api = AsyncMock()
        mock_api.async_login = AsyncMock(return_value="test_token")
        mock_api.async_get_user_info = AsyncMock(
            return_value={"data": {}}  # 没有 userName
        )
        
        with patch("custom_components.guangzhou_gas.config_flow.GuangzhouGasAPI", return_value=mock_api):
            config_flow.hass.async_get_clientsession = MagicMock(return_value=AsyncMock())
            
            result = await config_flow._test_connection(VALID_CONFIG.copy())
            
            assert result == (False, "cannot_get_user_info")
    
    @pytest.mark.asyncio
    async def test_test_connection_unexpected_error(self, config_flow: MockConfigFlow):
        """Test _test_connection with unexpected error."""
        # Mock API to raise unexpected error
        mock_api = AsyncMock()
        mock_api.async_login = AsyncMock(side_effect=Exception("Unexpected error"))
        
        with patch("custom_components.guangzhou_gas.config_flow.GuangzhouGasAPI", return_value=mock_api):
            config_flow.hass.async_get_clientsession = MagicMock(return_value=AsyncMock())
            
            result = await config_flow._test_connection(VALID_CONFIG.copy())
            
            assert result == (False, "unknown_error")
