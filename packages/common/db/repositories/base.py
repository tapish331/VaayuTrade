from __future__ import annotations

from typing import Any, List, Mapping, Optional

from sqlalchemy import Table, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """Generic CRUD operations using SQLAlchemy Core."""

    def __init__(self, session: AsyncSession, table: Table, id_column: str = "id") -> None:
        self.session = session
        self.table = table
        self.id_col = self.table.c[id_column]

    async def create(self, values: Mapping[str, Any]) -> Mapping[str, Any]:
        stmt = insert(self.table).values(**dict(values)).returning(self.table)
        res = await self.session.execute(stmt)
        return dict(res.mappings().one())

    async def get(self, id_: Any) -> Optional[Mapping[str, Any]]:
        stmt = select(self.table).where(self.id_col == id_)
        res = await self.session.execute(stmt)
        row = res.mappings().first()
        return dict(row) if row else None

    async def list(self, limit: int = 100, offset: int = 0) -> List[Mapping[str, Any]]:
        stmt = select(self.table).limit(limit).offset(offset)
        res = await self.session.execute(stmt)
        return [dict(m) for m in res.mappings().all()]

    async def update(self, id_: Any, values: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
        stmt = (
            update(self.table)
            .where(self.id_col == id_)
            .values(**dict(values))
            .returning(self.table)
        )
        res = await self.session.execute(stmt)
        row = res.mappings().first()
        return dict(row) if row else None

    async def delete(self, id_: Any) -> int:
        stmt = delete(self.table).where(self.id_col == id_)
        res = await self.session.execute(stmt)
        return res.rowcount or 0
