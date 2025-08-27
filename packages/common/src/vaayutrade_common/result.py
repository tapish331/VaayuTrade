from __future__ import annotations
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, field_validator
from .errors import AppError

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    ok: bool
    value: Optional[T] = None
    error: Optional[AppError] = None

    @field_validator("value", "error")
    @classmethod
    def _one_of(cls, v, info):
        # Validation happens in model_post_init; keep individual field validators permissive.
        return v

    def model_post_init(self, _ctx) -> None:
        if self.ok and self.error is not None:
            raise ValueError("ok=True cannot have error")
        if not self.ok and self.value is not None:
            raise ValueError("ok=False cannot have value")
        if self.ok is False and self.error is None:
            raise ValueError("ok=False requires error")

def Ok(value: T) -> Result[T]:
    return Result[T](ok=True, value=value)

def Err(error: AppError) -> Result[None]:
    return Result[None](ok=False, error=error)
