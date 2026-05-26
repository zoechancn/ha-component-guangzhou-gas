"""Guangzhou Gas API Client."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout
from homeassistant.core import HomeAssistant

from .const import (
    API_LOGIN_URL,
    API_USER_INFO_URL,
    API_GAS_DETAIL_URL,
    DEFAULT_HEADERS,
)
from .exceptions import (
    GuangzhouGasAPIError,
    GuangzhouGasAuthError,
    GuangzhouGasConnectionError,
    GuangzhouGasDataError,
)

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 10  # 请求超时时间（秒）
MAX_RETRIES = 3  # 最大重试次数


class GuangzhouGasAPI:
    """Guangzhou Gas API Client."""
    
    def __init__(
        self,
        session: aiohttp.ClientSession,
        nickname: str,
        accept_key: str,
        unionid: str,
    ) -> None:
        """Initialize the API client.
        
        Args:
            session: aiohttp ClientSession.
            nickname: User nickname.
            accept_key: User accept key.
            unionid: User union ID.
        """
        self._session = session
        self._nickname = nickname
        self._accept_key = accept_key
        self._unionid = unionid
        self._token: str | None = None
        
    async def async_login(self) -> str:
        """Login and get token.
        
        Returns:
            Token string.
            
        Raises:
            GuangzhouGasAuthError: Authentication failed.
            GuangzhouGasConnectionError: Connection failed.
            GuangzhouGasAPIError: API error.
        """
        _LOGGER.debug("Logging in as %s", self._nickname)
        
        # 根据 Node-RED 流程，登录时使用表单格式
        # nickName 和 acceptKey 放在 body，unionid 放在 header
        data = f"nickName={self._nickname}&acceptKey={self._accept_key}"
        
        headers = {
            **DEFAULT_HEADERS,
            "unionid": self._unionid,
            "xweb_xhr": "1",
        }
        
        try:
            response = await self._async_request_form(API_LOGIN_URL, data, headers)
            
            # 根据 Node-RED：let token = res.data;
            # Token 是直接存在 data 字段里（字符串），不是 data.token
            token = response.get("data")
            
            if not token or not isinstance(token, str):
                _LOGGER.error("Token not found in response: %s", response)
                raise GuangzhouGasDataError("Token not found in response")
            
            self._token = token
            _LOGGER.debug("Login successful, token: %s...", token[:10])
            return token
            
        except GuangzhouGasAPIError as err:
            _LOGGER.error("Login failed: %s", err)
            raise
            
    async def async_get_user_info(self, token: str) -> dict[str, Any]:
        """Get user info.
        
        Args:
            token: Authentication token.
            
        Returns:
            User info data.
            
        Raises:
            GuangzhouGasConnectionError: Connection failed.
            GuangzhouGasAPIError: API error.
        """
        _LOGGER.debug("Getting user info")
        
        # 根据 Node-RED：msg.payload = '{}';
        data = "{}"
        
        headers = {
            **DEFAULT_HEADERS,
            "unionid": self._unionid,
            "xweb_xhr": "1",
            "accessToken": token,  # ← 关键：Node-RED 用 accessToken，不是 Authorization
        }
        
        try:
            response = await self._async_request_form(API_USER_INFO_URL, data, headers)
            _LOGGER.debug("User info received: %s", response.get("data"))
            return response
            
        except GuangzhouGasAPIError as err:
            _LOGGER.error("Get user info failed: %s", err)
            raise
            
    async def async_get_gas_detail(self, token: str, user_no: str) -> dict[str, Any]:
        """Get gas detail.
        
        Args:
            token: Authentication token.
            user_no: User number (for query).
            
        Returns:
            Gas detail data.
            
        Raises:
            GuangzhouGasConnectionError: Connection failed.
            GuangzhouGasAPIError: API error.
        """
        _LOGGER.debug("Getting gas detail for user %s", user_no)
        
        # 根据 Node-RED：msg.payload = 'userno=' + encodeURIComponent(userInfo.userNo);
        data = f"userno={user_no}"
        
        headers = {
            **DEFAULT_HEADERS,
            "unionid": self._unionid,
            "xweb_xhr": "1",
            "accessToken": token,
        }
        
        try:
            response = await self._async_request_form(API_GAS_DETAIL_URL, data, headers)
            _LOGGER.debug("Gas detail received: %s", response.get("data"))
            return response
            
        except GuangzhouGasAPIError as err:
            _LOGGER.error("Get gas detail failed: %s", err)
            raise
    
    async def _async_request_form(
        self,
        url: str,
        data: str,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Make HTTP request with form data (x-www-form-urlencoded).
        
        Args:
            url: Request URL.
            data: Request data (form encoded string).
            headers: Request headers.
            
        Returns:
            JSON response data.
            
        Raises:
            GuangzhouGasAuthError: Authentication failed.
            GuangzhouGasConnectionError: Connection failed.
            GuangzhouGasAPIError: API error.
        """
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with async_timeout.timeout(TIMEOUT):
                    _LOGGER.debug("Sending POST request to %s with data: %s", url, data)
                    _LOGGER.debug("Headers: %s", {k: v for k, v in headers.items() if k.lower() not in ["unionid", "accesstoken"]})
                    
                    response = await self._session.post(
                        url,
                        data=data,  # 表单格式（字符串）
                        headers=headers,
                    )
                
                # 检查 HTTP 状态码
                response.raise_for_status()
                
                # 先记录响应内容（用于调试）
                response_text = await response.text()
                _LOGGER.debug("Response status: %s", response.status)
                _LOGGER.debug("Response headers: %s", dict(response.headers))
                _LOGGER.debug("Response text: %s", response_text[:1000])
                
                # 尝试解析 JSON（忽略 Content-Type 检查）
                try:
                    json_data = await response.json(content_type=None)
                except Exception as json_err:
                    _LOGGER.error("Failed to parse JSON (attempt %d/%d): %s", 
                                 attempt, MAX_RETRIES, json_err)
                    _LOGGER.error("Response text: %s", response_text[:1000])
                    if attempt == MAX_RETRIES:
                        raise GuangzhouGasAPIError(f"Failed to parse JSON: {json_err}") from json_err
                    continue
                
                _LOGGER.debug("Response JSON: %s", json_data)
                
                # 检查 API 返回的状态
                # 根据 Node-RED，成功时返回 {code: 200, data: {...}}
                # 注意：不同 API 可能使用不同的字段名
                api_code = json_data.get("code", json_data.get("status", json_data.get("errcode")))
                api_msg = json_data.get("msg", json_data.get("message", json_data.get("errmsg", "")))
                
                _LOGGER.debug("API response - code: %s, msg: %s", api_code, api_msg)
                
                # 判断成功条件
                is_success = (
                    api_code == 200 
                    or str(api_code) == "0" 
                    or api_code is True 
                    or api_code is None  # 有些 API 成功时不返回 code 字段
                    or (isinstance(json_data, dict) and "data" in json_data)  # 有 data 字段可能是成功
                )
                
                if not is_success:
                    # 构造详细错误信息（包含完整响应）
                    error_detail = f"{api_msg}" if api_msg else f"API returned: {json_data}"
                    error_msg = f"{error_detail} (code: {api_code})"
                    
                    _LOGGER.error("API error (attempt %d/%d): %s", 
                                 attempt, MAX_RETRIES, error_msg)
                    
                    # 如果是认证错误，直接抛出异常
                    error_str = str(error_detail).lower()
                    if "认证" in error_str or "登录" in error_str or "token" in error_str or "auth" in error_str:
                        raise GuangzhouGasAuthError(f"Authentication failed: {error_detail}")
                    
                    # 如果是最后一次重试，抛出异常
                    if attempt == MAX_RETRIES:
                        raise GuangzhouGasAPIError(f"API error: {error_msg}")
                    
                    # 否则重试
                    continue
                
                return json_data
                
            except aiohttp.ClientResponseError as err:
                _LOGGER.error("HTTP error (attempt %d/%d): %s", 
                             attempt, MAX_RETRIES, err)
                if attempt == MAX_RETRIES:
                    raise GuangzhouGasConnectionError(f"HTTP error: {err}") from err
                
            except aiohttp.ClientError as err:
                _LOGGER.error("Connection error (attempt %d/%d): %s", 
                             attempt, MAX_RETRIES, err)
                if attempt == MAX_RETRIES:
                    raise GuangzhouGasConnectionError(f"Connection failed: {err}") from err
                
            except asyncio.TimeoutError:
                _LOGGER.error("Request timeout (attempt %d/%d)", 
                             attempt, MAX_RETRIES)
                if attempt == MAX_RETRIES:
                    raise GuangzhouGasConnectionError("Request timeout") from None
            
            # 重试前等待（指数退避）
            if attempt < MAX_RETRIES:
                wait_time = 2 ** (attempt - 1)  # 1, 2, 4 秒
                _LOGGER.info("Retrying in %d seconds...", wait_time)
                await asyncio.sleep(wait_time)
        
        # 理论上不会执行到这里
        raise GuangzhouGasAPIError("Max retries exceeded")
