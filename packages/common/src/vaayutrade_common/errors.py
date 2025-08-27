from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    VALIDATION = "validation"
    BROKER_REJECT = "broker_reject"
    BROKER_RATE_LIMIT = "broker_rate_limit"
    RISK_HALT = "risk_halt"
    NOT_TRADABLE = "not_tradable"
    STALE_FEED = "stale_feed"
    CONFIG_INVALID = "config_invalid"
    TIMEOUT = "timeout"
    NETWORK = "network"
    INTERNAL = "internal"


class AppError(BaseModel):
    code: ErrorCode
    message: str
    retryable: bool = False
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Optional[Mapping[str, Any]] = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    @classmethod
    def from_exception(
        cls, exc: Exception, code: ErrorCode = ErrorCode.INTERNAL, retryable: bool = False
    ) -> "AppError":
        return cls(code=code, message=str(exc), retryable=retryable)
