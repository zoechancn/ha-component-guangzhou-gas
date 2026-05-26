"""Pytest configuration and fixtures for Guangzhou Gas tests."""
from __future__ import annotations

import json
import pytest
import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import aiohttp
from aiohttp import ClientSession, ClientResponse
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.guangzhou_gas.const import (
    DOMAIN,
    CONF_NICKNAME,
    CONF_ACCEPT_KEY,
    CONF_UNIONID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)
from custom_components.guangzhou_gas.api import GuangzhouGasAPI
from custom_components.guangzhou_gas.coordinator import GuangzhouGasDataUpdateCoordinator


# 测试配置数据
MOCK_CONFIG = {
    CONF_NICKNAME: "test_user",
    CONF_ACCEPT_KEY: "test_accept_key",
    CONF_UNIONID: "test_unionid",
    CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
}

# 模拟 API 响应数据
MOCK_LOGIN_RESPONSE = {
    "code": 200,
    "msg": " success ",
    "data": {
        "token": "eyJhbGciOiJIUzI1NiJ9.test.token"
    }
}

MOCK_USER_INFO_RESPONSE = {
    "code": 200,
    "msg": " success ",
    "data": {
        "userName": "测试用户",
        "userNo": "711111111",
        "userAddress": "广州市天河区测试路1号",
        "money": "100.50",
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

MOCK_GAS_DETAIL_RESPONSE = {
    "code": 200,
    "msg": " success ",
    "data": {
        "userNo": "711111111",
        "userName": "测试用户",
        "userAddress": "广州市天河区测试路1号",
        "money": "100.50",
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


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Return mock config data."""
    return MOCK_CONFIG.copy()


@pytest.fixture
def mock_login_response() -> Dict[str, Any]:
    """Return mock login response."""
    return MOCK_LOGIN_RESPONSE.copy()


@pytest.fixture
def mock_user_info_response() -> Dict[str, Any]:
    """Return mock user info response."""
    return MOCK_USER_INFO_RESPONSE.copy()


@pytest.fixture
def mock_gas_detail_response() -> Dict[str, Any]:
    """Return mock gas detail response."""
    return MOCK_GAS_DETAIL_RESPONSE.copy()


@pytest.fixture
def mock_api_data() -> Dict[str, Any]:
    """Return merged mock API data (user info + gas detail)."""
    data = {}
    data.update(MOCK_USER_INFO_RESPONSE["data"])
    data.update(MOCK_GAS_DETAIL_RESPONSE["data"])
    return data


@pytest.fixture
async def mock_session() -> AsyncMock:
    """Create a mock aiohttp ClientSession."""
    session = AsyncMock(spec=ClientSession)
    return session


@pytest.fixture
def api_client(mock_session: AsyncMock) -> GuangzhouGasAPI:
    """Create an API client with mock session."""
    return GuangzhouGasAPI(
        mock_session,
        MOCK_CONFIG[CONF_NICKNAME],
        MOCK_CONFIG[CONF_ACCEPT_KEY],
        MOCK_CONFIG[CONF_UNIONID],
    )


@pytest.fixture
def mock_config_entry() -> ConfigEntry:
    """Create a mock ConfigEntry."""
    entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title="广州燃气 - 测试用户",
        data=MOCK_CONFIG,
        source="user",
        state=1,  # ConfigEntryState.LOADED
        unique_id="test_unique_id",
    )
    return entry


@pytest.fixture
async def hass() -> HomeAssistant:
    """Create a Home Assistant instance for testing."""
    hass = HomeAssistant()
    yield hass
    await hass.async_stop()


@pytest.fixture
def mock_coordinator(
    hass: HomeAssistant,
    api_client: GuangzhouGasAPI,
) -> GuangzhouGasDataUpdateCoordinator:
    """Create a mock coordinator."""
    coordinator = GuangzhouGasDataUpdateCoordinator(
        hass,
        api_client,
        DEFAULT_SCAN_INTERVAL,
    )
    return coordinator


def load_fixture(filename: str) -> Dict[str, Any]:
    """Load a fixture file."""
    import os
    fixture_path = os.path.join(
        os.path.dirname(__file__),
        "fixtures",
        filename,
    )
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)
