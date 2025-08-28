from __future__ import annotations

from typing import Any, Mapping, Optional

from sqlalchemy import Table, select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository


class ConfigRepository(BaseRepository):
    def __init__(self, session: AsyncSession, config: Table) -> None:
        super().__init__(session, config, id_column="id")

    async def get_active(self, key: str = "trading") -> Optional[Mapping[str, Any]]:
        stmt = select(self.table).where(
            (self.table.c.key == key) & (self.table.c.is_active.is_(True))
        )
        res = await self.session.execute(stmt)
        row = res.mappings().first()
        return dict(row) if row else None
