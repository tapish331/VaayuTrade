from __future__ import annotations

import os
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def to_async_url(url: str) -> str:
    """Normalize postgres URLs to asyncpg dialect."""
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql+psycopg://") or url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.split("://", 1)[1]
    return url


def get_database_url() -> str:
    url: Optional[str] = os.getenv("DATABASE_URL")
    if not url or not url.strip():
        raise RuntimeError("DATABASE_URL is required (use postgresql+asyncpg://...)")
    return to_async_url(url)


def create_engine() -> AsyncEngine:
    return create_async_engine(
        get_database_url(),
        pool_pre_ping=False,
        pool_size=5,
        max_overflow=10,
    )


def create_session_factory(
    engine: Optional[AsyncEngine] = None,
) -> async_sessionmaker[AsyncSession]:
    eng = engine or create_engine()
    return async_sessionmaker(eng, expire_on_commit=False)
