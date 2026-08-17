"""Exceptions for Guangzhou Gas integration."""

from __future__ import annotations


class GuangzhouGasAPIError(Exception):
    """Base exception for Guangzhou Gas API errors."""


class GuangzhouGasAuthError(GuangzhouGasAPIError):
    """Exception for authentication failures."""


class GuangzhouGasConnectionError(GuangzhouGasAPIError):
    """Exception for connection failures."""


class GuangzhouGasDataError(GuangzhouGasAPIError):
    """Exception for data parsing failures."""
