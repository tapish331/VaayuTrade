from __future__ import annotations

from typing import Any, Mapping, Optional

from sqlalchemy import Table, select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository


class OrderRepository(BaseRepository):
    def __init__(self, session: AsyncSession, order: Table) -> None:
        super().__init__(session, order, id_column="id")

    async def get_by_client_id(self, client_id: str) -> Optional[Mapping[str, Any]]:
        stmt = select(self.table).where(self.table.c.client_id == client_id)
        res = await self.session.execute(stmt)
        row = res.mappings().first()
        return dict(row) if row else None
