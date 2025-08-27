import pytest
from vaayutrade_common import Order, OrderType, OrderSide


def test_limit_requires_price():
    with pytest.raises(ValueError):
        Order(client_id="cid", symbol="TCS", side=OrderSide.BUY, qty=1, type=OrderType.LIMIT)


def test_sl_limit_requires_price_and_trigger():
    with pytest.raises(ValueError):
        Order(
            client_id="cid",
            symbol="TCS",
            side=OrderSide.BUY,
            qty=1,
            type=OrderType.SL_LIMIT,
            limit_price=100.0,
        )
