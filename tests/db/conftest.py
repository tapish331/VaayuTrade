from __future__ import annotations

import pytest_asyncio
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from packages.common.db.session import (
    create_engine,
    get_database_url,
    make_session_for_connection,
)

pytest_plugins = ("pytest_asyncio",)


def _alembic_upgrade_head_sync() -> None:
    cfg = AlembicConfig("infra/db/alembic.ini")
    cfg.set_main_option("sqlalchemy.url", get_database_url())
    alembic_command.upgrade(cfg, "head")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _migrate_db() -> None:
    import anyio

    await anyio.to_thread.run_sync(_alembic_upgrade_head_sync)


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncEngine:
    eng = create_engine(echo=False)
    try:
        async with eng.connect() as conn:
            await conn.execute(text("SELECT 1"))
        yield eng
    finally:
        await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine: AsyncEngine) -> AsyncSession:
    async with engine.connect() as conn:
        trans = await conn.begin()
        session = make_session_for_connection(conn)
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()
