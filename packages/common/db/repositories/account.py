from __future__ import annotations

from sqlalchemy import Table
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository


class AccountRepository(BaseRepository):
    def __init__(self, session: AsyncSession, account: Table) -> None:
        super().__init__(session, account, id_column="id")
