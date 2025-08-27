from datetime import datetime, timezone
from uuid import uuid4

from vaayutrade_common import (
    Account,
    Instrument,
    Universe,
    Signal,
    Order,
    OrderSide,
    OrderType,
    Execution,
    Position,
    RiskLimit,
    PnLMinute,
    ModelArtifact,
    FeatureSnapshot,
    Candle,
    PriceLevel,
    TickSnapshot,
    AlertEvent,
    AlertSeverity,
    BacktestRun,
    ConfigBlob,
)


def roundtrip(obj):
    s = obj.model_dump_json()
    return obj.__class__.model_validate_json(s)


def test_account_roundtrip():
    obj = Account(api_key_ref="aws:secrets:KITE")
    assert roundtrip(obj) == obj


def test_instrument_roundtrip():
    obj = Instrument(token=123, symbol="TCS", tick_size=0.05, lot_size=1)
    assert roundtrip(obj) == obj


def test_universe_roundtrip():
    obj = Universe(name="NIFTY100", symbols=["TCS", "INFY"])
    assert roundtrip(obj) == obj


def test_signal_roundtrip():
    obj = Signal(symbol="TCS", score=0.72, side=OrderSide.BUY, conf=0.66)
    assert roundtrip(obj) == obj


def test_order_limit_roundtrip():
    obj = Order(
        client_id="cid-1",
        symbol="TCS",
        side=OrderSide.BUY,
        qty=10,
        type=OrderType.LIMIT,
        limit_price=100.5,
    )
    assert roundtrip(obj) == obj


def test_execution_roundtrip():
    obj = Execution(order_id=uuid4(), qty=5, price=100.0)
    assert roundtrip(obj) == obj


def test_position_roundtrip():
    obj = Position(symbol="TCS", net_qty=10, avg_price=100.0, mtm=1.5)
    assert roundtrip(obj) == obj


def test_risklimit_roundtrip():
    obj = RiskLimit(
        max_daily_loss=0.015, per_trade_risk=0.0035, max_positions=10, max_spread_bps=12
    )
    assert roundtrip(obj) == obj


def test_pnlminute_roundtrip():
    obj = PnLMinute(
        ts=datetime.now(timezone.utc), realized=10.0, unrealized=-2.0, fees=0.5, turnover=100000
    )
    assert roundtrip(obj) == obj


def test_modelartifact_roundtrip():
    obj = ModelArtifact(
        version="1.0.0",
        path="s3://models/model.onnx",
        schema_hash="abcd1234",
        metrics={"auc": 0.71},
        calib={"iso_rmse": 0.04},
    )
    assert roundtrip(obj) == obj


def test_featuresnapshot_roundtrip():
    obj = FeatureSnapshot(ts=datetime.now(timezone.utc), symbol="TCS", features={"rsi": 55.2})
    assert roundtrip(obj) == obj


def test_candle_roundtrip():
    obj = Candle(
        symbol="TCS",
        ts=datetime.now(timezone.utc),
        o=100,
        h=110,
        low=95,
        c=105,
        v=100000,
        vwap=103.2,
    )
    assert roundtrip(obj) == obj


def test_ticksnapshot_roundtrip():
    obj = TickSnapshot(
        ts=datetime.now(timezone.utc),
        symbol="TCS",
        bids=[PriceLevel(price=100.0, qty=50)],
        asks=[PriceLevel(price=100.1, qty=60)],
        last=100.05,
        volume=12345,
    )
    assert roundtrip(obj) == obj


def test_alertevent_roundtrip():
    obj = AlertEvent(
        ts=datetime.now(timezone.utc),
        type="squareoff.warn",
        severity=AlertSeverity.WARN,
        payload={"t": "15:10"},
    )
    assert roundtrip(obj) == obj


def test_backtestrun_roundtrip():
    obj = BacktestRun(
        config_ref="cfg:2025-08-01",
        metrics={"sharpe": 1.2},
        trades=[{"symbol": "TCS", "r": 0.5}],
        seed=42,
    )
    assert roundtrip(obj) == obj


def test_configblob_roundtrip():
    obj = ConfigBlob(version="v1", data={"risk": {"max_daily_loss": 0.015}})
    assert roundtrip(obj) == obj
