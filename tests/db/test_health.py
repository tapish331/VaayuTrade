from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from packages.common.db.health import check_db


@pytest.mark.asyncio
async def test_health_ok(engine: AsyncEngine) -> None:
    health = await check_db(engine)
    assert health.ok
    assert any(name == "connect" and ok for name, ok, _ in health.checks)
    assert any(name == "alembic" for name, _, _ in health.checks)
