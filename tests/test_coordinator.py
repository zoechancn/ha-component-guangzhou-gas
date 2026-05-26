"""Tests for Guangzhou Gas data update coordinator."""
from __future__ import annotations

import pytest
from typing import Any, Dict, Optional
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    ConfigEntryAuthFailed,
    UpdateFailed,
)

from custom_components.guangzhou_gas.coordinator import GuangzhouGasDataUpdateCoordinator
from custom_components.guangzhou_gas.api import GuangzhouGasAPI
from custom_components.guangzhou_gas.const import DEFAULT_SCAN_INTERVAL
from custom_components.guangzhou_gas.exceptions import (
    GuangzhouGasAuthError,
    GuangzhouGasConnectionError,
    GuangzhouGasAPIError,
)


# 模拟 API 响应数据
MOCK_USER_INFO = {
    "code": 200,
    "msg": "success",
    "data": {
        "userName": "测试用户",
        "userNo": "711111111",
        "userAddress": "广州市天河区测试路1号",
        "money": "100.50",
    }
}

MOCK_GAS_DETAIL = {
    "code": 200,
    "msg": "success",
    "data": {
        "userNo": "711111111",
        "bm": "BM11111111",
        "blx": "IC卡表",
        "rqbztdes": "正常",
        "jieti_interval": "2024-01-01 至 2024-12-31",
        "jieti_amount_benci": "120",
        "lastRecordWatchNum": "1000",
        "lastRecordWatchDate": "2024-01-15",
        "zhczje": "200",
        "zhczsj": "20240520143000",
        "ljczye": "500",
        "feeWay": "银行代扣",
        "safeInspectHas": "已安检"
    }
}

MERGED_DATA = {
    **MOCK_USER_INFO["data"],
    **MOCK_GAS_DETAIL["data"],
}


class MockHomeAssistant:
    """Mock HomeAssistant for testing."""
    
    def __init__(self):
        """Initialize mock HA."""
        self.data = {}
        self.bus = MagicMock()
        self.services = MagicMock()
        self.states = MagicMock()


@pytest.fixture
def mock_hass() -> MockHomeAssistant:
    """Create a mock HomeAssistant instance."""
    return MockHomeAssistant()


@pytest.fixture
def mock_api() -> AsyncMock:
    """Create a mock API client."""
    api = AsyncMock(spec=GuangzhouGasAPI)
    api.async_login = AsyncMock(return_value="test_token_12345")
    api.async_get_user_info = AsyncMock(return_value=MOCK_USER_INFO)
    api.async_get_gas_detail = AsyncMock(return_value=MOCK_GAS_DETAIL)
    return api


@pytest.fixture
def coordinator(
    mock_hass: MockHomeAssistant,
    mock_api: AsyncMock,
) -> GuangzhouGasDataUpdateCoordinator:
    """Create a coordinator instance."""
    return GuangzhouGasDataUpdateCoordinator(
        mock_hass,
        mock_api,
        DEFAULT_SCAN_INTERVAL,
    )


class TestGuangzhouGasDataUpdateCoordinator:
    """Test GuangzhouGasDataUpdateCoordinator."""
    
    # ==================== 初始化测试 ====================
    
    def test_coordinator_init(
        self,
        mock_hass: MockHomeAssistant,
        mock_api: AsyncMock,
    ):
        """Test coordinator initialization."""
        coord = GuangzhouGasDataUpdateCoordinator(
            mock_hass,
            mock_api,
            DEFAULT_SCAN_INTERVAL,
        )
        
        assert coord._api == mock_api
        assert coord._scan_interval == DEFAULT_SCAN_INTERVAL
        assert coord.name == "guangzhou_gas"
        assert coord.update_interval == timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    
    # ==================== _async_update_data 成功测试 ====================
    
    @pytest.mark.asyncio
    async def test_async_update_data_success(
        self,
        coordinator: GuangzhouGasDataUpdateCoordinator,
        mock_api: AsyncMock,
    ):
        """Test successful data update."""
        # 设置 mock 返回值
        mock_api.async_login.return_value = "test_token"
        mock_api.async_get_user_info.return_value = MOCK_USER_INFO
        mock_api.async_get_gas_detail.return_value = MOCK_GAS_DETAIL
        
        # 执行更新
        result = await coordinator._async_update_data()
        
        # 验证结果
        assert result is not None
        assert result["userName"] == "测试用户"
        assert result["userNo"] == "711111111"
        assert result["money"] == "100.50"
        assert result["bm"] == "BM11111111"
        
        # 验证 API 调用顺序
        mock_api.async_login.assert_called_once()
        mock_api.async_get_user_info.assert_called_once_with("test_token")
        mock_api.async_get_gas_detail.assert_called_once_with("test_token")
    
    @pytest.mark.asyncio
    async def test_async_update_data_merge(
        self,
        coordinator: GuangzhouGasDataUpdateCoordinator,
        mock_api: AsyncMock,
    ):
        """Test data merge from user info and gas detail."""
        # user_info 和 gas_detail 有不同的数据
        user_info = {
            "code": 200,
            "data": {"userName": "测试用户", "money": "100.50"}
        }
        gas_detail = {
            "code": 200,
            "data": {"bm": "BM11111111", "blx": "IC卡表"}
        }
        
        mock_api.async_get_user_info.return_value = user_info
        mock_api.async_get_gas_detail.return_value = gas_detail
        
        # 执行更新
        result = await coordinator._async_update_data()
        
        # 验证数据合并
        assert result["userName"] == "测试用户"
        assert result["money"] == "100.50"
        assert result["bm"] == "BM11111111"
        assert result["blx"] == "IC卡表"
    
    # ==================== _async_update_data 错误处理测试 ====================
    
    @pytest.mark.asyncio
    async def test_async_update_data_auth_error(
        self,
        coordinator: GuangzhouGasDataUpdateCoordinator,
        mock_api: AsyncMock,
    ):
        """Test data update with auth error."""
        # Mock 登录失败
        mock_api.async_login.side_effect = GuangzhouGasAuthError("Authentication failed")
        
        # 验证抛出 ConfigEntryAuthFailed
        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()
    
    @pytest.mark.asyncio
    async def test_async_update_data_connection_error_on_login(
        self,
        coordinator: GuangzhouGasDataUpdateCoordinator,
        mock_api: AsyncMock,
    ):
        """Test data update with connection error during login."""
        # Mock 登录时连接失败
        mock_api.async_login.side_effect = GuangzhouGasConnectionError("Connection failed")
        
        # 验证抛出 UpdateFailed
        with pytest.raises(UpdateFailed) as exc_info:
            await coordinator._async_update_data()
        
        assert "Connection failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_async_update_data_connection_error_on_user_info(
        self,
        coordinator: GuangzhouGasDataUpdateCoordinator,
        mock_api: AsyncMock,
    ):
        """Test data update with connection error during get_user_info."""
        # 登录成功，但获取用户信息时连接失败
        mock_api.async_login.return_value = "test_token"
        mock_api.async_get_user_info.side_effect = GuangzhouGasConnectionError("Connection failed")
        
        # 验证抛出 UpdateFailed
        with pytest.raises(UpdateFailed) as exc_info:
            await coordinator._async_update_data()
        
        assert "Connection failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_async_update_data_connection_error_on_gas_detail(
        self,
        coordinator: GuangzhouGasDataUpdateCoordinator,
        mock_api: AsyncMock,
    ):
        """Test data update with connection error during get_gas_detail."""
        # 登录和获取用户信息成功，但获取燃气详情时连接失败
        mock_api.async_login.return_value = "test_token"
        mock_api.async_get_user_info.return_value = MOCK_USER_INFO
        mock_api.async_get_gas_detail.side_effect = GuangzhouGasConnectionError("Connection failed")
        
        # 验证抛出 UpdateFailed
        with pytest.raises(UpdateFailed) as exc_info:
            await coordinator._async_update_data()
        
        assert "Connection failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_async_update_data_api_error(
        self,
        coordinator: GuangzhouGasDataUpdateCoordinator,
        mock_api: AsyncMock,
    ):
        """Test data update with API error."""
        # Mock API 错误
        mock_api.async_login.return_value = "test_token"
        mock_api.async_get_user_info.return_value = MOCK_USER_INFO
        mock_api.async_get_gas_detail.side_effect = GuangzhouGasAPIError("API error")
        
        # 验证抛出 UpdateFailed
        with pytest.raises(UpdateFailed) as exc_info:
            await coordinator._async_update_data()
        
        assert "API error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_async_update_data_unexpected_error(
        self,
        coordinator: GuangzhouGasDataUpdateCoordinator,
        mock_api: AsyncMock,
    ):
        """Test data update with unexpected error."""
        # Mock 意外错误
        mock_api.async_login.side_effect = Exception("Unexpected error")
        
        # 验证抛出 UpdateFailed
        with pytest.raises(UpdateFailed) as exc_info:
            await coordinator._async_update_data()
        
        assert "Unexpected error" in str(exc_info.value)
    
    # ==================== 更新间隔测试 ====================
    
    def test_update_interval(
        self,
        mock_hass: MockHomeAssistant,
        mock_api: AsyncMock,
    ):
        """Test update interval setting."""
        # 测试默认间隔
        coord = GuangzhouGasDataUpdateCoordinator(
            mock_hass,
            mock_api,
            DEFAULT_SCAN_INTERVAL,
        )
        assert coord.update_interval == timedelta(seconds=DEFAULT_SCAN_INTERVAL)
        
        # 测试自定义间隔
        custom_interval = 3600  # 1小时
        coord = GuangzhouGasDataUpdateCoordinator(
            mock_hass,
            mock_api,
            custom_interval,
        )
        assert coord.update_interval == timedelta(seconds=custom_interval)
