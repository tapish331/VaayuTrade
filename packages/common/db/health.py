from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


@dataclass(frozen=True)
class DBHealth:
    ok: bool
    checks: List[Tuple[str, bool, str]]


async def check_db(engine: AsyncEngine) -> DBHealth:
    checks: List[Tuple[str, bool, str]] = []

    async with engine.connect() as conn:
        # connectivity
        try:
            await conn.execute(text("SELECT 1"))
            checks.append(("connect", True, "ok"))
        except Exception as e:  # pragma: no cover
            checks.append(("connect", False, str(e)))

        # alembic head
        try:
            res = await conn.execute(text("SELECT version_num FROM alembic_version"))
            head = res.scalar_one()
            checks.append(("alembic", True, head))
        except Exception as e:
            checks.append(("alembic", False, str(e)))

        required = {
            "account",
            "instrument",
            "order",
            "execution",
            "position",
            "signal",
            "config",
        }
        try:
            res = await conn.execute(
                text(
                    """
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema='public'
                    """
                )
            )
            have = {r[0] for r in res}
            missing = sorted(required - have)
            checks.append(
                ("tables", not missing, "missing: " + ",".join(missing) if missing else "ok")
            )
        except Exception as e:
            checks.append(("tables", False, str(e)))

    overall = all(ok for _, ok, _ in checks)
    return DBHealth(ok=overall, checks=checks)
