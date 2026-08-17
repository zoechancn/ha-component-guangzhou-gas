"""Asynchronous client for the Guangzhou Gas mini-program API."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Mapping
from typing import Any

import aiohttp
import async_timeout

from .const import API_GAS_DETAIL_URL, API_LOGIN_URL, API_USER_INFO_URL, DEFAULT_HEADERS
from .exceptions import (
    GuangzhouGasAPIError,
    GuangzhouGasAuthError,
    GuangzhouGasConnectionError,
    GuangzhouGasDataError,
)

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = 15
MAX_RETRIES = 3


class GuangzhouGasAPI:
    """Client for the endpoints used by the Guangzhou Gas mini program."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        nickname: str,
        accept_key: str,
        unionid: str,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._nickname = nickname
        self._accept_key = accept_key
        self._unionid = unionid

    def _headers(self, token: str | None = None) -> dict[str, str]:
        """Build request headers without exposing credentials in logs."""
        headers = {**DEFAULT_HEADERS, "unionid": self._unionid}
        if token:
            headers["accessToken"] = token
        return headers

    async def async_login(self) -> str:
        """Authenticate and return a short-lived access token."""
        response = await self._async_request_form(
            API_LOGIN_URL,
            {"nickName": self._nickname, "acceptKey": self._accept_key},
            self._headers(),
        )
        token = response.get("data")
        if not isinstance(token, str) or not token:
            raise GuangzhouGasDataError("The login response did not contain a token")
        return token

    async def async_get_user_info(self, token: str) -> dict[str, Any]:
        """Return the bound gas account selected by the mini program."""
        response = await self._async_request_form(
            API_USER_INFO_URL,
            {},
            self._headers(token),
        )
        data = response.get("data")
        if not isinstance(data, Mapping):
            raise GuangzhouGasDataError("User response did not contain an object")
        return self._extract_record(data.get("wtVo"), "wtVo")

    async def async_get_gas_detail(self, token: str, user_no: str) -> dict[str, Any]:
        """Return meter, balance and recharge information for an account."""
        response = await self._async_request_form(
            API_GAS_DETAIL_URL,
            {"userno": user_no},
            self._headers(token),
        )
        data = response.get("data")
        if not isinstance(data, Mapping):
            raise GuangzhouGasDataError("Meter response did not contain an object")

        meter = self._extract_record(data.get("rqbList"), "rqbList")
        # Some useful totals live beside rqbList rather than inside it.
        return {
            **{key: value for key, value in data.items() if key != "rqbList"},
            **meter,
        }

    @staticmethod
    def _extract_record(value: Any, field: str) -> dict[str, Any]:
        """Accept the object and one-item-list variants used by the API."""
        if isinstance(value, Mapping):
            return dict(value)
        if isinstance(value, list) and value and isinstance(value[0], Mapping):
            return dict(value[0])
        raise GuangzhouGasDataError(f"{field} did not contain a usable record")

    async def _async_request_form(
        self,
        url: str,
        data: Mapping[str, str],
        headers: Mapping[str, str],
    ) -> dict[str, Any]:
        """POST an encoded form and return a validated JSON object."""
        last_error: Exception | None = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with (
                    async_timeout.timeout(REQUEST_TIMEOUT),
                    self._session.post(url, data=data, headers=headers) as response,
                ):
                    if response.status in {401, 403}:
                        raise GuangzhouGasAuthError("Authentication was rejected")
                    response.raise_for_status()
                    payload = await response.json(content_type=None)

                if not isinstance(payload, dict):
                    raise GuangzhouGasDataError("API response was not a JSON object")
                self._validate_response(payload)
                return payload

            except GuangzhouGasAuthError:
                raise
            except GuangzhouGasAPIError:
                raise
            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
                last_error = err
                if attempt == MAX_RETRIES:
                    break
                delay = 2 ** (attempt - 1)
                _LOGGER.debug(
                    "Guangzhou Gas request failed; retrying in %s seconds (%s/%s)",
                    delay,
                    attempt,
                    MAX_RETRIES,
                )
                await asyncio.sleep(delay)

        raise GuangzhouGasConnectionError(
            f"Request failed after {MAX_RETRIES} attempts: {last_error}"
        ) from last_error

    @staticmethod
    def _validate_response(payload: Mapping[str, Any]) -> None:
        """Convert mini-program error envelopes into integration exceptions."""
        code = payload.get("code")
        errcode = payload.get("errcode")
        is_error = payload.get("error") is True
        successful = code in {None, 0, 200, "0", "200"} and errcode in {
            None,
            0,
            "0",
        }
        if successful and not is_error:
            return

        message = str(
            payload.get("errmsg")
            or payload.get("msg")
            or payload.get("message")
            or "Unknown API error"
        )
        normalized = message.lower()
        if any(word in normalized for word in ("认证", "登录", "token", "auth")):
            raise GuangzhouGasAuthError(message)
        raise GuangzhouGasAPIError(message)
