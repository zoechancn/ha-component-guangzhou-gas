"""Exceptions for Guangzhou Gas integration."""
from __future__ import annotations


class GuangzhouGasAPIError(Exception):
    """Base exception for Guangzhou Gas API errors."""
    pass


class GuangzhouGasAuthError(GuangzhouGasAPIError):
    """Exception for authentication failures."""
    pass


class GuangzhouGasConnectionError(GuangzhouGasAPIError):
    """Exception for connection failures."""
    pass


class GuangzhouGasDataError(GuangzhouGasAPIError):
    """Exception for data parsing failures."""
    pass
