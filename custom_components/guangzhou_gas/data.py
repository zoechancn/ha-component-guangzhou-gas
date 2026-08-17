"""Normalization helpers for Guangzhou Gas API values."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from zoneinfo import ZoneInfo

LOCAL_TIME_ZONE = ZoneInfo("Asia/Shanghai")


def clean_value(value: Any) -> Any:
    """Return a useful scalar value or None for API placeholders."""
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if not value or value.lower() in {"none", "null", "undefined", "--"}:
            return None
    return value


def decimal_value(value: Any) -> Decimal | None:
    """Convert an API number without introducing floating-point noise."""
    value = clean_value(value)
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def date_value(value: Any) -> date | None:
    """Parse the date formats returned by Guangzhou Gas."""
    value = clean_value(value)
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    for pattern in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y%m%d"):
        try:
            return (
                datetime.strptime(str(value), pattern)
                .replace(tzinfo=LOCAL_TIME_ZONE)
                .date()
            )
        except ValueError:
            continue
    return None


def datetime_value(value: Any) -> datetime | None:
    """Parse a Guangzhou local timestamp into an aware datetime."""
    value = clean_value(value)
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = None
        for pattern in ("%Y%m%d%H%M%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(str(value), pattern).replace(
                    tzinfo=LOCAL_TIME_ZONE
                )
                break
            except ValueError:
                continue
        if parsed is None:
            return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=LOCAL_TIME_ZONE)


def first_value(data: Mapping[str, Any], keys: tuple[str, ...]) -> Any:
    """Return the first meaningful value for a list of API field aliases."""
    for key in keys:
        value = clean_value(data.get(key))
        if value is not None:
            return value
    return None
