from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Mapping, Optional
from uuid import UUID, uuid4

from pydantic import Field, constr, model_validator
from .base import VM

# --- Core domain models (aligned with Discovery §3) ---

class Account(VM):
    id: UUID = Field(default_factory=uuid4)
    broker: Literal["zerodha"] = "zerodha"
    api_key_ref: str
    product: Literal["MIS"] = "MIS"
    timezone: str = "Asia/Kolkata"

class Instrument(VM):
    token: int
    symbol: constr(strip_whitespace=True, min_length=1)
    exchange: Literal["NSE"] = "NSE"
    tick_size: float
    lot_size: int = 1
    is_tradable: bool = True

class Universe(VM):
    id: UUID = Field(default_factory=uuid4)
    name: str
    symbols: List[str]
    ban_lists: List[str] = []

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    SL_LIMIT = "SL_LIMIT"  # Stop-loss limit

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"

class Signal(VM):
    id: UUID = Field(default_factory=uuid4)
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    symbol: str
    score: float
    horizon: int = 10  # minutes
    side: OrderSide
    conf: float = 0.5
    features_ref: Optional[str] = None

class Order(VM):
    id: UUID = Field(default_factory=uuid4)
    client_id: str
    symbol: str
    side: OrderSide
    qty: int
    type: OrderType = OrderType.LIMIT
    limit_price: Optional[float] = None
    trigger: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    parent_id: Optional[UUID] = None

    @model_validator(mode="after")
    def _validate_pricing(self) -> "Order":
        if self.type == OrderType.LIMIT and self.limit_price is None:
            raise ValueError("LIMIT order requires limit_price")
        if self.type == OrderType.SL_LIMIT and (self.limit_price is None or self.trigger is None):
            raise ValueError("SL_LIMIT order requires both limit_price and trigger")
        return self

class Execution(VM):
    id: UUID = Field(default_factory=uuid4)
    order_id: UUID
    qty: int
    price: float
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    liquidity_flag: Optional[Literal["M", "T"]] = None  # Maker/Taker

class Position(VM):
    symbol: str
    net_qty: int
    avg_price: float
    mtm: float = 0.0
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RiskLimit(VM):
    max_daily_loss: float
    per_trade_risk: float
    max_positions: int
    max_spread_bps: float

class PnLMinute(VM):
    ts: datetime
    realized: float
    unrealized: float
    fees: float
    turnover: float

class ModelArtifact(VM):
    id: UUID = Field(default_factory=uuid4)
    version: str
    path: str
    schema_hash: str
    metrics: Mapping[str, float] = {}
    calib: Mapping[str, float] = {}

class FeatureSnapshot(VM):
    ts: datetime
    symbol: str
    features: Mapping[str, float]

class Candle(VM):
    symbol: str
    ts: datetime
    o: float
    h: float
    l: float
    c: float
    v: float
    vwap: Optional[float] = None

class PriceLevel(VM):
    price: float
    qty: int

class TickSnapshot(VM):
    ts: datetime
    symbol: str
    bids: List[PriceLevel]  # depth 1..5
    asks: List[PriceLevel]
    last: Optional[float] = None
    volume: Optional[int] = None

class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"

class AlertEvent(VM):
    ts: datetime
    type: str
    severity: AlertSeverity = AlertSeverity.INFO
    payload: Dict[str, Any] = {}

class BacktestRun(VM):
    id: UUID = Field(default_factory=uuid4)
    config_ref: str
    metrics: Mapping[str, float] = {}
    trades: List[Mapping[str, Any]] = []
    seed: Optional[int] = None

class ConfigBlob(VM):
    version: str
    data: Dict[str, Any]

# --- end models ---
