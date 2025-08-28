from __future__ import annotations

from typing import Iterable, Optional, Union

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

TABLES = (
    "account",
    "instrument",
    "signal",
    "order",
    "execution",
    "position",
    "pnl_minute",
    "model_artifact",
    "config",
    "alert",
    "backtest_run",
    "audit_event",
)


async def reflect_all(
    engine: Union[AsyncEngine, AsyncConnection],
    only: Optional[Iterable[str]] = None,
) -> MetaData:
    """Reflect database tables once per process."""
    md = MetaData()

    async def _do_reflect(conn: AsyncConnection) -> None:
        def _reflect(sync_conn):
            md.reflect(bind=sync_conn, only=list(only) if only else TABLES)

        await conn.run_sync(_reflect)

    if isinstance(engine, AsyncEngine):
        async with engine.begin() as conn:
            await _do_reflect(conn)
    else:
        await _do_reflect(engine)

    return md
