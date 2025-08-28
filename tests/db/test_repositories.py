from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.common.db.metadata_reflect import reflect_all
from packages.common.db.repositories.account import AccountRepository
from packages.common.db.repositories.config import ConfigRepository
from packages.common.db.repositories.instrument import InstrumentRepository
from packages.common.db.repositories.order import OrderRepository


@pytest.mark.asyncio
async def test_account_crud(session: AsyncSession) -> None:
    md = await reflect_all(session.bind)
    account = md.tables["account"]
    repo = AccountRepository(session, account)
    created = await repo.create(
        {
            "broker": "ZERODHA",
            "product": "MIS",
            "api_key_ref": "secret://kite",
        }
    )
    fetched = await repo.get(created["id"])
    assert fetched and fetched["broker"] == "ZERODHA"
    updated = await repo.update(created["id"], {"is_active": False})
    assert updated and updated["is_active"] is False
    deleted = await repo.delete(created["id"])
    assert deleted == 1


@pytest.mark.asyncio
async def test_instrument_and_order_helpers(session: AsyncSession) -> None:
    md = await reflect_all(session.bind)
    irepo = InstrumentRepository(session, md.tables["instrument"])
    orepo = OrderRepository(session, md.tables["order"])

    sym = await irepo.create(
        {
            "token": 12345,
            "symbol": "INFY",
            "exchange": "NSE",
            "tick_size": "0.05",
            "lot_size": 1,
        }
    )
    got = await irepo.get_by_symbol("INFY")
    assert got and got["id"] == sym["id"]

    acc = await AccountRepository(session, md.tables["account"]).create(
        {"broker": "ZERODHA", "product": "MIS", "api_key_ref": "k"}
    )
    ord1 = await orepo.create(
        {
            "account_id": acc["id"],
            "instrument_id": sym["id"],
            "client_id": "cid-1",
            "side": "BUY",
            "type": "LIMIT",
            "qty": 10,
            "limit_price": "100.00",
            "status": "NEW",
        }
    )
    by_client = await orepo.get_by_client_id("cid-1")
    assert by_client and by_client["id"] == ord1["id"]


@pytest.mark.asyncio
async def test_config_active(session: AsyncSession) -> None:
    md = await reflect_all(session.bind)
    crepo = ConfigRepository(session, md.tables["config"])
    await crepo.create({"key": "trading", "version": 1, "yaml": "a: 1", "is_active": True})
    active = await crepo.get_active("trading")
    assert active and active["version"] == 1
