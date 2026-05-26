"""Tests for Guangzhou Gas API client."""
from __future__ import annotations

import asyncio
import json
import pytest
from typing import Any, Dict
from unittest.mock import AsyncMock, patch, MagicMock

import aiohttp
from aiohttp import ClientResponse, ClientResponseError
from homeassistant.exceptions import ConfigEntryAuthFailed

from custom_components.guangzhou_gas.api import GuangzhouGasAPI
from custom_components.guangzhou_gas.const import (
    API_LOGIN_URL,
    API_USER_INFO_URL,
    API_GAS_DETAIL_URL,
)
from custom_components.guangzhou_gas.exceptions import (
    GuangzhouGasAuthError,
    GuangzhouGasConnectionError,
    GuangzhouGasAPIError,
    GuangzhouGasDataError,
)


class MockClientResponse:
    """Mock aiohttp.ClientResponse."""
    
    def __init__(self, status: int, data: Dict[str, Any], headers: Dict[str, str] = None):
        """Initialize mock response."""
        self.status = status
        self._data = data
        self.headers = headers or {}
        self._json_called = False
    
    async def json(self) -> Dict[str, Any]:
        """Return JSON data."""
        self._json_called = True
        return self._data
    
    async def raise_for_status(self) -> None:
        """Raise exception if status is not successful."""
        if self.status >= 400:
            raise aiohttp.ClientResponseError(
                request_info=MagicMock(),
                history=(),
                status=self.status,
                message="HTTP Error",
            )
    
    def __aenter__(self):
        return self
    
    def __aexit__(self, exc_type, exc_val, exc_tb):
        return False


class MockClientSession:
    """Mock aiohttp.ClientSession."""
    
    def __init__(self, responses: Dict[str, MockClientResponse] = None):
        """Initialize mock session."""
        self.responses = responses or {}
        self.requests = []
    
    async def post(self, url: str, **kwargs) -> MockClientResponse:
        """Mock POST request."""
        self.requests.append({"method": "POST", "url": url, **kwargs})
        if url in self.responses:
            return self.responses[url]
        # Default success response
        return MockClientResponse(200, {"code": 200, "msg": "success", "data": {}})
    
    async def get(self, url: str, **kwargs) -> MockClientResponse:
        """Mock GET request."""
        self.requests.append({"method": "GET", "url": url, **kwargs})
        if url in self.responses:
            return self.responses[url]
        # Default success response
        return MockClientResponse(200, {"code": 200, "msg": "success", "data": {}})


@pytest.fixture
def mock_session() -> MockClientSession:
    """Create a mock session."""
    return MockClientSession()


@pytest.fixture
def api_client(mock_session: MockClientSession) -> GuangzhouGasAPI:
    """Create an API client with mock session."""
    return GuangzhouGasAPI(
        mock_session,
        "test_nickname",
        "test_accept_key",
        "test_unionid",
    )


class TestGuangzhouGasAPI:
    """Test class for GuangzhouGasAPI."""
    
    # ==================== async_login 测试 ====================
    
    @pytest.mark.asyncio
    async def test_login_success(self, api_client: GuangzhouGasAPI, mock_session: MockClientSession):
        """Test successful login."""
        # 模拟成功登录响应
        mock_response = MockClientResponse(
            200,
            {"code": 200, "msg": "success", "data": {"token": "test_token_12345"}}
        )
        mock_session.responses = {API_LOGIN_URL: mock_response}
        
        # 执行登录
        token = await api_client.async_login()
        
        # 验证结果
        assert token == "test_token_12345"
        assert api_client._token == "test_token_12345"
        
        # 验证请求被正确调用
        assert len(mock_session.requests) >= 1
        post_request = [r for r in mock_session.requests if r["url"] == API_LOGIN_URL][0]
        assert post_request["method"] == "POST"
        assert post_request["json"]["nickName"] == "test_nickname"
        assert post_request["json"]["acceptKey"] == "test_accept_key"
        assert post_request["json"]["unionid"] == "test_unionid"
    
    @pytest.mark.asyncio
    async def test_login_auth_failed(self, api_client: GuangzhouGasAPI, mock_session: MockClientSession):
        """Test login with authentication failure."""
        # 模拟认证失败响应
        mock_response = MockClientResponse(
            200,
            {"code": 401, "msg": "认证失败，请重新登录", "data": None}
        )
        mock_session.responses = {API_LOGIN_URL: mock_response}
        
        # 验证抛出认证错误
        with pytest.raises(GuangzhouGasAuthError) as exc_info:
            await api_client.async_login()
        
        assert "Authentication failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_login_api_error(self, api_client: GuangzhouGasAPI, mock_session: MockClientSession):
        """Test login with API error (non-auth)."""
        # 模拟 API 错误响应
        mock_response = MockClientResponse(
            200,
            {"code": 500, "msg": "服务器内部错误", "data": None}
        )
        mock_session.responses = {API_LOGIN_URL: mock_response}
        
        # 验证抛出 API 错误
        with pytest.raises(GuangzhouGasAPIError) as exc_info:
            await api_client.async_login()
        
        assert "API error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_login_token_not_found(self, api_client: GuangzhouGasAPI, mock_session: MockClientSession):
        """Test login when token is not in response."""
        # 模拟响应中没有 token
        mock_response = MockClientResponse(
            200,
            {"code": 200, "msg": "success", "data": {"user_id": "123"}}
        )
        mock_session.responses = {API_LOGIN_URL: mock_response}
        
        # 验证抛出数据错误
        with pytest.raises(GuangzhouGasDataError) as exc_info:
            await api_client.async_login()
        
        assert "Token not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_login_http_error(self, api_client: GuangzhouGasAPI, mock_session: MockClientSession):
        """Test login with HTTP error."""
        # 模拟 HTTP 错误响应
        mock_response = MockClientResponse(
            500,
            {"code": 500, "msg": "Internal Server Error", "data": None}
        )
        mock_session.responses = {API_LOGIN_URL: mock_response}
        
        # 验证抛出连接错误
        with pytest.raises(GuangzhouGasConnectionError) as exc_info:
            await api_client.async_login()
        
        assert "HTTP error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_login_connection_error(self, api_client: GuangzhouGasAPI):
        """Test login with connection error."""
        # 创建一个会抛出连接的 session
        class FailingSession(MockClientSession):
            async def post(self, url: str, **kwargs):
                raise aiohttp.ClientError("Connection failed")
        
        api_client._session = FailingSession()
        
        # 验证抛出连接错误（经过重试后）
        with pytest.raises(GuangzhouGasConnectionError) as exc_info:
            await api_client.async_login()
        
        assert "Connection failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_login_timeout(self, api_client: GuangzhouGasAPI):
        """Test login with timeout."""
        import asyncio
        
        # 创建一个会超时的 session
        class TimeoutSession(MockClientSession):
            async def post(self, url: str, **kwargs):
                raise asyncio.TimeoutError()
        
        api_client._session = TimeoutSession()
        
        # 验证抛出连接错误（经过重试后）
        with pytest.raises(GuangzhouGasConnectionError) as exc_info:
            await api_client.async_login()
        
        assert "Request timeout" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_login_retry_mechanism(self, api_client: GuangzhouGasAPI, mock_session: MockClientSession):
        """Test login retry mechanism (max 3 retries)."""
        # 创建计数器来跟踪调用次数
        call_count = 0
        
        class RetrySession(MockClientSession):
            async def post(self, url: str, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count < 3:  # 前两次失败
                    raise aiohttp.ClientError("Temporary failure")
                # 第三次成功
                return MockClientResponse(
                    200,
                    {"code": 200, "msg": "success", "data": {"token": "test_token"}}
                )
        
        api_client._session = RetrySession()
        
        # 验证最终成功
        token = await api_client.async_login()
        assert token == "test_token"
        assert call_count == 3  # 重试了3次
    
    # ==================== async_get_user_info 测试 ====================
    
    @pytest.mark.asyncio
    async def test_get_user_info_success(self, api_client: GuangzhouGasAPI, mock_session: MockClientSession):
        """Test successful get user info."""
        # 先设置 token
        api_client._token = "test_token"
        
        # 模拟成功响应
        mock_response = MockClientResponse(
            200,
            {
                "code": 200,
                "msg": "success",
                "data": {
                    "userName": "测试用户",
                    "userNo": "711111111",
                }
            }
        )
        mock_session.responses = {API_USER_INFO_URL: mock_response}
        
        # 执行获取用户信息
        result = await api_client.async_get_user_info("test_token")
        
        # 验证结果
        assert result["code"] == 200
        assert result["data"]["userName"] == "测试用户"
        assert result["data"]["userNo"] == "711111111"
        
        # 验证请求头包含 Authorization
        post_request = [r for r in mock_session.requests if r["url"] == API_USER_INFO_URL][0]
        assert "Authorization" in post_request["headers"]
        assert post_request["headers"]["Authorization"] == "Bearer test_token"
    
    @pytest.mark.asyncio
    async def test_get_user_info_auth_error(self, api_client: GuangzhouGasAPI, mock_session: MockClientSession):
        """Test get user info with auth error."""
        api_client._token = "invalid_token"
        
        # 模拟认证失败
        mock_response = MockClientResponse(
            200,
            {"code": 401, "msg": "认证失败，请重新登录", "data": None}
        )
        mock_session.responses = {API_USER_INFO_URL: mock_response}
        
        # 验证抛出认证错误
        with pytest.raises(GuangzhouGasAuthError):
            await api_client.async_get_user_info("invalid_token")
    
    @pytest.mark.asyncio
    async def test_get_user_info_connection_error(self, api_client: GuangzhouGasAPI):
        """Test get user info with connection error."""
        api_client._token = "test_token"
        
        class FailingSession(MockClientSession):
            async def post(self, url: str, **kwargs):
                raise aiohttp.ClientError("Connection failed")
        
        api_client._session = FailingSession()
        
        # 验证抛出连接错误
        with pytest.raises(GuangzhouGasConnectionError):
            await api_client.async_get_user_info("test_token")
    
    # ==================== async_get_gas_detail 测试 ====================
    
    @pytest.mark.asyncio
    async def test_get_gas_detail_success(self, api_client: GuangzhouGasAPI, mock_session: MockClientSession):
        """Test successful get gas detail."""
        api_client._token = "test_token"
        
        # 模拟成功响应
        mock_response = MockClientResponse(
            200,
            {
                "code": 200,
                "msg": "success",
                "data": {
                    "userNo": "711111111",
                    "money": "100.50",
                    "bm": "BM11111111",
                }
            }
        )
        mock_session.responses = {API_GAS_DETAIL_URL: mock_response}
        
        # 执行获取燃气详情
        result = await api_client.async_get_gas_detail("test_token")
        
        # 验证结果
        assert result["code"] == 200
        assert result["data"]["money"] == "100.50"
        
        # 验证请求头包含 Authorization
        post_request = [r for r in mock_session.requests if r["url"] == API_GAS_DETAIL_URL][0]
        assert "Authorization" in post_request["headers"]
    
    @pytest.mark.asyncio
    async def test_get_gas_detail_auth_error(self, api_client: GuangzhouGasAPI, mock_session: MockClientSession):
        """Test get gas detail with auth error."""
        api_client._token = "invalid_token"
        
        # 模拟认证失败
        mock_response = MockClientResponse(
            200,
            {"code": 401, "msg": "登录已过期", "data": None}
        )
        mock_session.responses = {API_GAS_DETAIL_URL: mock_response}
        
        # 验证抛出认证错误
        with pytest.raises(GuangzhouGasAuthError):
            await api_client.async_get_gas_detail("invalid_token")
    
    @pytest.mark.asyncio
    async def test_get_gas_detail_connection_error(self, api_client: GuangzhouGasAPI):
        """Test get gas detail with connection error."""
        api_client._token = "test_token"
        
        class FailingSession(MockClientSession):
            async def post(self, url: str, **kwargs):
                raise aiohttp.ClientError("Connection failed")
        
        api_client._session = FailingSession()
        
        # 验证抛出连接错误
        with pytest.raises(GuangzhouGasConnectionError):
            await api_client.async_get_gas_detail("test_token")
    
    # ==================== _async_request 测试 ====================
    
    @pytest.mark.asyncio
    async def test_async_request_retry_on_api_error(self, api_client: GuangzhouGasAPI, mock_session: MockClientSession):
        """Test _async_request retry mechanism on API errors."""
        # 第一次返回错误，第二次成功
        responses = [
            MockClientResponse(200, {"code": 500, "msg": "Server error", "data": None}),
            MockClientResponse(200, {"code": 200, "msg": "success", "data": {"token": "test"}}),
        ]
        
        original_post = mock_session.post
        call_count = 0
        
        async def post_with_retry(url, **kwargs):
            nonlocal call_count
            if call_count < len(responses):
                resp = responses[call_count]
                call_count += 1
                return resp
            return await original_post(url, **kwargs)
        
        mock_session.post = post_with_retry
        
        # 执行请求（应该重试并成功）
        result = await api_client._async_request("POST", API_LOGIN_URL, {})
        
        assert result["code"] == 200
        assert call_count == 2  # 调用了两次
