"""Tests for Guangzhou Gas value normalization."""

from datetime import date
from decimal import Decimal

from custom_components.guangzhou_gas.data import (
    clean_value,
    date_value,
    datetime_value,
    decimal_value,
    first_value,
)


def test_clean_value_removes_api_placeholders() -> None:
    """Blank and placeholder strings should not become entity states."""
    assert clean_value("  ") is None
    assert clean_value("null") is None
    assert clean_value(" -- ") is None
    assert clean_value("正常") == "正常"


def test_decimal_value_is_exact() -> None:
    """Money and meter readings should avoid float rounding."""
    assert decimal_value("163.55") == Decimal("163.55")
    assert decimal_value("not-a-number") is None


def test_date_value_accepts_api_formats() -> None:
    """Date entities should receive native date values."""
    assert date_value("2026-06-13 00:00:00") == date(2026, 6, 13)
    assert date_value("20260613") == date(2026, 6, 13)
    assert date_value("invalid") is None


def test_datetime_value_adds_guangzhou_timezone() -> None:
    """Timestamp entities require timezone-aware datetime values."""
    value = datetime_value("20260512211243")
    assert value is not None
    assert value.isoformat() == "2026-05-12T21:12:43+08:00"


def test_first_value_supports_api_aliases() -> None:
    """Field aliases should tolerate API casing and spelling changes."""
    data = {"old": None, "new": "使用"}
    assert first_value(data, ("old", "new")) == "使用"
