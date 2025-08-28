from __future__ import annotations

from typing import Any, Mapping, Optional

from sqlalchemy import Table, select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository


class InstrumentRepository(BaseRepository):
    def __init__(self, session: AsyncSession, instrument: Table) -> None:
        super().__init__(session, instrument, id_column="id")

    async def get_by_symbol(self, symbol: str) -> Optional[Mapping[str, Any]]:
        stmt = select(self.table).where(self.table.c.symbol == symbol)
        res = await self.session.execute(stmt)
        row = res.mappings().first()
        return dict(row) if row else None
