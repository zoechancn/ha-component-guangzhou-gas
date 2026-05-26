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
        
        # 尝试两种格式：JSON 和表单
        data_json = {
            "nickName": self._nickname,
            "acceptKey": self._accept_key,
            "unionid": self._unionid,
        }
        
        data_form = {
            "nickName": self._nickname,
            "acceptKey": self._accept_key,
            "unionid": self._unionid,
        }
        
        # 先尝试 JSON 格式
        try:
            _LOGGER.debug("Trying JSON format")
            response = await self._async_request("POST", API_LOGIN_URL, data_json)
            token = response.get("data", {}).get("token")
            
            if not token:
                _LOGGER.error("Token not found in response: %s", response)
                raise GuangzhouGasDataError("Token not found in response")
            
            self._token = token
            _LOGGER.debug("Login successful (JSON), token: %s...", token[:10])
            return token
            
        except GuangzhouGasAPIError as err:
            _LOGGER.warning("JSON format failed, trying form format: %s", err)
            
            # 尝试表单格式
            try:
                _LOGGER.debug("Trying form format")
                response = await self._async_request_form(API_LOGIN_URL, data_form)
                token = response.get("data", {}).get("token")
                
                if not token:
                    _LOGGER.error("Token not found in response (form): %s", response)
                    raise GuangzhouGasDataError("Token not found in response")
                
                self._token = token
                _LOGGER.debug("Login successful (form), token: %s...", token[:10])
                return token
                
            except Exception as form_err:
                _LOGGER.error("Both JSON and form formats failed")
                raise GuangzhouGasAPIError(f"Login failed: {form_err}") from form_err
    
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
        
        headers = {
            **DEFAULT_HEADERS,
            "Authorization": f"Bearer {token}",
        }
        
        try:
            response = await self._async_request(
                "POST", API_USER_INFO_URL, {}, headers
            )
            _LOGGER.debug("User info received: %s", response.get("data"))
            return response
            
        except GuangzhouGasAPIError:
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error getting user info: %s", err)
            raise GuangzhouGasAPIError(f"Unexpected error: {err}") from err
    
    async def async_get_gas_detail(self, token: str) -> dict[str, Any]:
        """Get gas detail.
        
        Args:
            token: Authentication token.
            
        Returns:
            Gas detail data.
            
        Raises:
            GuangzhouGasConnectionError: Connection failed.
            GuangzhouGasAPIError: API error.
        """
        _LOGGER.debug("Getting gas detail")
        
        headers = {
            **DEFAULT_HEADERS,
            "Authorization": f"Bearer {token}",
        }
        
        try:
            response = await self._async_request(
                "POST", API_GAS_DETAIL_URL, {}, headers
            )
            _LOGGER.debug("Gas detail received: %s", response.get("data"))
            return response
            
        except GuangzhouGasAPIError:
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error getting gas detail: %s", err)
            raise GuangzhouGasAPIError(f"Unexpected error: {err}") from err
    
    async def _async_request(
        self,
        method: str,
        url: str,
        data: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request with retry.
        
        Args:
            method: HTTP method (GET, POST, etc.).
            url: Request URL.
            data: Request data (for POST).
            headers: Request headers (optional).
            
        Returns:
            JSON response data.
            
        Raises:
            GuangzhouGasAuthError: Authentication failed.
            GuangzhouGasConnectionError: Connection failed.
            GuangzhouGasAPIError: API error.
        """
        headers = headers or DEFAULT_HEADERS
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with async_timeout.timeout(TIMEOUT):
                    if method.upper() == "POST":
                        # 先尝试 JSON 格式
                        _LOGGER.debug("Sending POST request to %s with JSON data: %s", url, data)
                        response = await self._session.post(
                            url,
                            json=data,
                            headers=headers,
                        )
                    else:
                        _LOGGER.debug("Sending GET request to %s with params: %s", url, data)
                        response = await self._session.get(
                            url,
                            params=data,
                            headers=headers,
                        )
                
                # 检查 HTTP 状态码
                response.raise_for_status()
                
                # 先记录响应内容（用于调试）
                response_text = await response.text()
                _LOGGER.debug("Response status: %s", response.status)
                _LOGGER.debug("Response headers: %s", dict(response.headers))
                _LOGGER.debug("Response text (first 500 chars): %s", response_text[:500])
                
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
                
                # 检查 API 返回的状态码
                if isinstance(json_data, dict) and json_data.get("code") != 200:
                    error_msg = json_data.get("msg", "Unknown error")
                    _LOGGER.error("API error (attempt %d/%d): %s", 
                                 attempt, MAX_RETRIES, error_msg)
                    
                    # 如果是认证错误，直接抛出异常
                    if "认证" in error_msg or "登录" in error_msg:
                        raise GuangzhouGasAuthError(f"Authentication failed: {error_msg}")
                    
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
    
    async def _async_request_form(
        self,
        url: str,
        data: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request with form data (x-www-form-urlencoded).
        
        Args:
            url: Request URL.
            data: Request data (for POST, will be sent as form data).
            headers: Request headers (optional).
            
        Returns:
            JSON response data.
            
        Raises:
            GuangzhouGasAuthError: Authentication failed.
            GuangzhouGasConnectionError: Connection failed.
            GuangzhouGasAPIError: API error.
        """
        headers = headers or DEFAULT_HEADERS
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with async_timeout.timeout(TIMEOUT):
                    _LOGGER.debug("Sending POST request (form) to %s with data: %s", url, data)
                    response = await self._session.post(
                        url,
                        data=data,  # 表单格式
                        headers=headers,
                    )
                
                # 检查 HTTP 状态码
                response.raise_for_status()
                
                # 先记录响应内容（用于调试）
                response_text = await response.text()
                _LOGGER.debug("Response status: %s", response.status)
                _LOGGER.debug("Response headers: %s", dict(response.headers))
                _LOGGER.debug("Response text (first 500 chars): %s", response_text[:500])
                
                # 尝试解析 JSON（忽略 Content-Type 检查）
                try:
                    json_data = await response.json(content_type=None)
                except Exception as json_err:
                    _LOGGER.error("Failed to parse JSON (form, attempt %d/%d): %s", 
                                 attempt, MAX_RETRIES, json_err)
                    _LOGGER.error("Response text: %s", response_text[:1000])
                    if attempt == MAX_RETRIES:
                        raise GuangzhouGasAPIError(f"Failed to parse JSON: {json_err}") from json_err
                    continue
                
                _LOGGER.debug("Response JSON (form): %s", json_data)
                
                # 检查 API 返回的状态码
                if isinstance(json_data, dict) and json_data.get("code") != 200:
                    error_msg = json_data.get("msg", "Unknown error")
                    _LOGGER.error("API error (form, attempt %d/%d): %s", 
                                 attempt, MAX_RETRIES, error_msg)
                    
                    # 如果是认证错误，直接抛出异常
                    if "认证" in error_msg or "登录" in error_msg:
                        raise GuangzhouGasAuthError(f"Authentication failed: {error_msg}")
                    
                    # 如果是最后一次重试，抛出异常
                    if attempt == MAX_RETRIES:
                        raise GuangzhouGasAPIError(f"API error: {error_msg}")
                    
                    # 否则重试
                    continue
                
                return json_data
                
            except aiohttp.ClientResponseError as err:
                _LOGGER.error("HTTP error (form, attempt %d/%d): %s", 
                             attempt, MAX_RETRIES, err)
                if attempt == MAX_RETRIES:
                    raise GuangzhouGasConnectionError(f"HTTP error: {err}") from err
                
            except aiohttp.ClientError as err:
                _LOGGER.error("Connection error (form, attempt %d/%d): %s", 
                             attempt, MAX_RETRIES, err)
                if attempt == MAX_RETRIES:
                    raise GuangzhouGasConnectionError(f"Connection failed: {err}") from err
                
            except asyncio.TimeoutError:
                _LOGGER.error("Request timeout (form, attempt %d/%d)", 
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
