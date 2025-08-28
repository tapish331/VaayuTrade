from __future__ import annotations

import os
from typing import Any, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool


def get_database_url() -> str:
    """Return a PostgreSQL URL guaranteed to use the asyncpg driver."""
    url: Optional[str] = os.getenv("DATABASE_URL")
    if not url or not url.strip():
        raise RuntimeError("DATABASE_URL is required (use postgresql+asyncpg://...)")
    if url.startswith("postgresql+psycopg://"):
        url = url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def create_engine(echo: bool = False) -> AsyncEngine:
    """
    Create an AsyncEngine. In CI/tests we default to NullPool to ensure each acquire
    gets a fresh connection and to avoid cross-task reuse that can trigger:
      asyncpg.InterfaceError: cannot perform operation: another operation is in progress
    Toggle via SQLALCHEMY_NULLPOOL_FOR_TESTS=0 to opt-out.
    """
    url = get_database_url()
    use_nullpool = os.getenv("SQLALCHEMY_NULLPOOL_FOR_TESTS", "1") == "1"
    kwargs: dict[str, Any] = {"echo": echo, "future": True}
    if use_nullpool:
        kwargs["poolclass"] = NullPool
    return create_async_engine(url, **kwargs)


def create_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
