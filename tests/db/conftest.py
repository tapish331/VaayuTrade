from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from packages.common.db.session import create_engine


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Ensure a single backend for pytest-asyncio auto mode."""
    return "asyncio"


@pytest.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    """Create engine and apply migrations for the test session."""
    eng = create_engine()
    cfg = Config("infra/db/alembic.ini")
    command.upgrade(cfg, "head")
    try:
        yield eng
    finally:
        command.downgrade(cfg, "base")


@pytest.fixture()
async def session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Provide a transactional AsyncSession per test."""
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.connect() as conn:
        trans = await conn.begin()
        async with sessionmaker(bind=conn) as s:
            nested = await s.begin_nested()

            @event.listens_for(s.sync_session, "after_transaction_end")
            def _restart_savepoint(sess, transaction) -> None:  # pragma: no cover
                if transaction.nested and not transaction._parent.nested:
                    from contextlib import suppress

                    with suppress(Exception):
                        sess.begin_nested()

            yield s

            await nested.rollback()
        await trans.rollback()
