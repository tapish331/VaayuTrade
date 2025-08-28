from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from packages.common.db.session import create_engine, create_session_factory


def _to_sync_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return "postgresql+psycopg://" + url.split("://", 1)[1]
    return url


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def engine() -> AsyncIterator[AsyncEngine]:
    eng = create_engine()
    alembic_cfg = Config("infra/db/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", _to_sync_url(os.environ["DATABASE_URL"]))
    command.upgrade(alembic_cfg, "head")
    try:
        yield eng
    finally:
        command.downgrade(alembic_cfg, "base")
        await eng.dispose()


@pytest_asyncio.fixture()
async def session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    session_factory = create_session_factory(engine)
    async with session_factory() as s:
        trans = await s.begin()
        nested = await s.begin_nested()
        try:
            yield s
        finally:
            await nested.rollback()
            await trans.rollback()
