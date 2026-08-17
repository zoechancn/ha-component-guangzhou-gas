"""Tests for Guangzhou Gas response validation."""

import asyncio
from typing import Any

import pytest

from custom_components.guangzhou_gas.api import GuangzhouGasAPI
from custom_components.guangzhou_gas.exceptions import (
    GuangzhouGasAPIError,
    GuangzhouGasAuthError,
    GuangzhouGasDataError,
)


def test_extract_record_accepts_object_and_list() -> None:
    """The production API alternates between object and list envelopes."""
    assert GuangzhouGasAPI._extract_record({"id": 1}, "record") == {"id": 1}
    assert GuangzhouGasAPI._extract_record([{"id": 2}], "record") == {"id": 2}


def test_extract_record_rejects_empty_value() -> None:
    """Missing records should fail clearly instead of creating blank sensors."""
    with pytest.raises(GuangzhouGasDataError):
        GuangzhouGasAPI._extract_record([], "record")


def test_validate_response_distinguishes_auth_error() -> None:
    """Expired credentials should trigger Home Assistant reauthentication."""
    with pytest.raises(GuangzhouGasAuthError):
        GuangzhouGasAPI._validate_response({"code": 401, "errmsg": "token失效"})


def test_validate_response_rejects_api_error() -> None:
    """Business API errors should not be treated as successful data."""
    with pytest.raises(GuangzhouGasAPIError):
        GuangzhouGasAPI._validate_response({"code": 500, "errmsg": "服务异常"})


def test_meter_detail_keeps_top_level_totals() -> None:
    """Balance totals outside rqbList must survive normalization."""

    class FixtureAPI(GuangzhouGasAPI):
        async def _async_request_form(self, *_: Any, **__: Any) -> dict[str, Any]:
            return {
                "code": 200,
                "data": {
                    "money": "113.6",
                    "rqbCount": "1",
                    "rqbList": [{"money": "61.85", "rqbbgh": "3303"}],
                },
            }

    api = FixtureAPI(None, "nickname", "key", "unionid")  # type: ignore[arg-type]
    result = asyncio.run(api.async_get_gas_detail("token", "3176411713"))
    assert result["money"] == "61.85"
    assert result["rqbCount"] == "1"
    assert result["rqbbgh"] == "3303"
