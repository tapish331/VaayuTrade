from __future__ import annotations

import os
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool


# ---------- URL helpers ----------


def get_database_url() -> str:
    url: Optional[str] = os.getenv("DATABASE_URL")
    if not url or not url.strip():
        raise RuntimeError("DATABASE_URL is required (sync: postgresql+psycopg:// ...)")
    return url


def to_async_url(url: str) -> str:
    """Normalize to an asyncpg URL for runtime use."""
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql+psycopg://"):
        return "postgresql+asyncpg://" + url.split("://", 1)[1]
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.split("://", 1)[1]
    return url


# ---------- Engine / session factories ----------


def create_engine(*, echo: bool = False) -> AsyncEngine:
    """Create a fresh AsyncEngine using a NullPool."""
    async_url = to_async_url(get_database_url())
    return create_async_engine(async_url, echo=echo, poolclass=NullPool, future=True)


SESSIONMAKER = async_sessionmaker(class_=AsyncSession, expire_on_commit=False)


def make_session_for_connection(conn: "AsyncConnection") -> AsyncSession:
    """Bind a new AsyncSession to the given AsyncConnection."""
    return SESSIONMAKER(bind=conn)
