"""Baseline Alembic migration: enums, tables, indexes, triggers."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_baseline_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # enums
    broker_enum = postgresql.ENUM("ZERODHA", name="broker_enum", create_type=False)
    exchange_enum = postgresql.ENUM("NSE", name="exchange_enum", create_type=False)
    product_enum = postgresql.ENUM("MIS", name="product_enum", create_type=False)
    order_side_enum = postgresql.ENUM("BUY", "SELL", name="order_side_enum", create_type=False)
    order_type_enum = postgresql.ENUM(
        "LIMIT", "SL_LIMIT", "MARKET", name="order_type_enum", create_type=False
    )
    order_status_enum = postgresql.ENUM(
        "NEW",
        "PENDING",
        "OPEN",
        "PARTIALLY_FILLED",
        "FILLED",
        "CANCELLED",
        "REJECTED",
        "EXPIRED",
        "TRIGGER_PENDING",
        name="order_status_enum",
        create_type=False,
    )
    signal_side_enum = postgresql.ENUM("LONG", "SHORT", name="signal_side_enum", create_type=False)
    liquidity_flag_enum = postgresql.ENUM(
        "PASSIVE", "AGGRESSIVE", "UNKNOWN", name="liquidity_flag_enum", create_type=False
    )
    alert_severity_enum = postgresql.ENUM(
        "INFO", "WARN", "CRITICAL", name="alert_severity_enum", create_type=False
    )

    enums = [
        broker_enum,
        exchange_enum,
        product_enum,
        order_side_enum,
        order_type_enum,
        order_status_enum,
        signal_side_enum,
        liquidity_flag_enum,
        alert_severity_enum,
    ]
    for enum in enums:
        enum.create(op.get_bind(), checkfirst=True)

    # account
    op.create_table(
        "account",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.Column("broker", broker_enum, nullable=False),
        sa.Column(
            "product",
            product_enum,
            nullable=False,
            server_default=sa.text("'MIS'"),
        ),
        sa.Column("timezone", sa.Text(), nullable=False, server_default=sa.text("'Asia/Kolkata'")),
        sa.Column("api_key_ref", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_account__broker", "account", ["broker"])

    # instrument
    op.create_table(
        "instrument",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("token", sa.BigInteger(), nullable=False),
        sa.Column("symbol", sa.Text(), nullable=False),
        sa.Column(
            "exchange",
            exchange_enum,
            nullable=False,
            server_default=sa.text("'NSE'"),
        ),
        sa.Column("tick_size", sa.Numeric(10, 6), nullable=False),
        sa.Column("lot_size", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("is_tradable", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_refreshed", sa.TIMESTAMP(timezone=True)),
        sa.UniqueConstraint("token", name="uq_instrument__token"),
        sa.UniqueConstraint("symbol", "exchange", name="uq_instrument__symbol_exchange"),
    )
    op.create_index("ix_instrument__is_tradable", "instrument", ["is_tradable"])
    op.create_index("ix_instrument__symbol", "instrument", ["symbol"])

    # model_artifact
    op.create_table(
        "model_artifact",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.Text(), nullable=False, server_default=sa.text("'primary'")),
        sa.Column("version", sa.Text(), nullable=False),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("schema_hash", sa.Text(), nullable=False),
        sa.Column("metrics", postgresql.JSONB()),
        sa.Column("calib", postgresql.JSONB()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("name", "version", name="uq_model_artifact__name_version"),
    )
    op.create_index("ix_model_artifact__is_active", "model_artifact", ["is_active"])

    # config
    op.create_table(
        "config",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("key", sa.Text(), nullable=False, server_default=sa.text("'trading'")),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("yaml", sa.Text(), nullable=False),
        sa.Column("json", postgresql.JSONB()),
        sa.Column("schema_hash", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("account.id", name="fk_config__account"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("key", "version", name="uq_config__key_version"),
    )
    op.create_index("ix_config__created_at_desc", "config", [sa.text("created_at DESC")])
    op.create_index(
        "uq_config__key_active",
        "config",
        ["key"],
        unique=True,
        postgresql_where=sa.text("is_active"),
    )

    # signal
    op.create_table(
        "signal",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("ts", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "instrument_id",
            sa.BigInteger(),
            sa.ForeignKey("instrument.id", name="fk_signal__instrument"),
            nullable=False,
        ),
        sa.Column("side", signal_side_enum, nullable=False),
        sa.Column("horizon_seconds", sa.SmallInteger(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float()),
        sa.Column("features_ref", sa.Text()),
        sa.Column(
            "model_artifact_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("model_artifact.id", name="fk_signal__model_artifact"),
            nullable=True,
        ),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index(
        "ix_signal__instrument_id_ts_desc",
        "signal",
        ["instrument_id", sa.text("ts DESC")],
    )
    op.create_index("ix_signal__ts_desc", "signal", [sa.text("ts DESC")])

    # order
    op.create_table(
        "order",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("account.id", name="fk_order__account"),
            nullable=False,
        ),
        sa.Column(
            "instrument_id",
            sa.BigInteger(),
            sa.ForeignKey("instrument.id", name="fk_order__instrument"),
            nullable=False,
        ),
        sa.Column(
            "signal_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("signal.id", name="fk_order__signal"),
            nullable=True,
        ),
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("order.id", name="fk_order__parent"),
            nullable=True,
        ),
        sa.Column("client_id", sa.String(64), nullable=False),
        sa.Column("broker_order_id", sa.String(64)),
        sa.Column("side", order_side_enum, nullable=False),
        sa.Column(
            "type",
            order_type_enum,
            nullable=False,
        ),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("limit_price", sa.Numeric(18, 6)),
        sa.Column("trigger_price", sa.Numeric(18, 6)),
        sa.Column(
            "status",
            order_status_enum,
            nullable=False,
            server_default=sa.text("'NEW'"),
        ),
        sa.Column("rejection_reason", sa.Text()),
        sa.Column(
            "placed_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("good_till", sa.TIMESTAMP(timezone=True)),
        sa.CheckConstraint("qty > 0", name="ck_order__qty_gt_zero"),
        sa.UniqueConstraint("client_id", name="uq_order__client_id"),
    )
    op.create_index(
        "ix_order__account_id_placed_at_desc",
        "order",
        ["account_id", sa.text("placed_at DESC")],
    )
    op.create_index("ix_order__instrument_id_status", "order", ["instrument_id", "status"])
    op.create_index(
        "ix_order__open",
        "order",
        ["instrument_id"],
        postgresql_where=sa.text(
            "status IN ('OPEN','PENDING','TRIGGER_PENDING','PARTIALLY_FILLED')"
        ),
    )
    op.create_index(
        "uq_order__broker_order_id",
        "order",
        ["broker_order_id"],
        unique=True,
        postgresql_where=sa.text("broker_order_id IS NOT NULL"),
    )

    # execution
    op.create_table(
        "execution",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "order_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("order.id", name="fk_execution__order", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ts", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(18, 6), nullable=False),
        sa.Column("trade_id", sa.Text()),
        sa.Column(
            "liquidity",
            liquidity_flag_enum,
            nullable=False,
            server_default=sa.text("'UNKNOWN'"),
        ),
        sa.CheckConstraint("qty > 0", name="ck_execution__qty_gt_zero"),
    )
    op.create_index("ix_execution__order_id_ts", "execution", ["order_id", "ts"])
    op.create_index("ix_execution__ts", "execution", ["ts"])
    op.create_index(
        "uq_execution__trade_id",
        "execution",
        ["trade_id"],
        unique=True,
        postgresql_where=sa.text("trade_id IS NOT NULL"),
    )

    # position
    op.create_table(
        "position",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("trading_day", sa.Date(), nullable=False),
        sa.Column(
            "instrument_id",
            sa.BigInteger(),
            sa.ForeignKey("instrument.id", name="fk_position__instrument"),
            nullable=False,
        ),
        sa.Column("net_qty", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("avg_price", sa.Numeric(18, 6), nullable=False, server_default=sa.text("0")),
        sa.Column("realized_pnl", sa.Numeric(18, 6), nullable=False, server_default=sa.text("0")),
        sa.Column("unrealized_pnl", sa.Numeric(18, 6), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "last_updated",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "trading_day", "instrument_id", name="uq_position__trading_day_instrument_id"
        ),
    )
    op.create_index("ix_position__instrument_id", "position", ["instrument_id"])
    op.create_index("ix_position__trading_day", "position", ["trading_day"])

    # pnl_minute
    op.create_table(
        "pnl_minute",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("ts", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "instrument_id",
            sa.BigInteger(),
            sa.ForeignKey("instrument.id", name="fk_pnl_minute__instrument"),
            nullable=True,
        ),
        sa.Column("realized", sa.Numeric(18, 6), nullable=False, server_default=sa.text("0")),
        sa.Column("unrealized", sa.Numeric(18, 6), nullable=False, server_default=sa.text("0")),
        sa.Column("fees", sa.Numeric(18, 6), nullable=False, server_default=sa.text("0")),
        sa.Column("turnover", sa.Numeric(18, 6), nullable=False, server_default=sa.text("0")),
        sa.UniqueConstraint("ts", "instrument_id", name="uq_pnl_minute__ts_instrument_id"),
    )
    op.create_index("ix_pnl_minute__ts", "pnl_minute", ["ts"])
    op.create_index("ix_pnl_minute__instrument_id_ts", "pnl_minute", ["instrument_id", "ts"])

    # alert
    op.create_table(
        "alert",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "ts", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("severity", alert_severity_enum, nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB()),
        sa.Column("dedup_key", sa.Text()),
        sa.Column("acked_at", sa.TIMESTAMP(timezone=True)),
        sa.Column(
            "acked_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("account.id", name="fk_alert__account"),
            nullable=True,
        ),
    )
    op.create_index("ix_alert__ts_desc", "alert", [sa.text("ts DESC")])
    op.create_index("ix_alert__severity_ts_desc", "alert", ["severity", sa.text("ts DESC")])
    op.create_index("ix_alert__type_ts_desc", "alert", ["type", sa.text("ts DESC")])
    op.create_index(
        "uq_alert__dedup_key",
        "alert",
        ["dedup_key"],
        unique=True,
        postgresql_where=sa.text("dedup_key IS NOT NULL"),
    )

    # backtest_run
    op.create_table(
        "backtest_run",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "config_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("config.id", name="fk_backtest_run__config"),
            nullable=True,
        ),
        sa.Column("seed", sa.Integer()),
        sa.Column("tag", sa.Text()),
        sa.Column("artifact_path", sa.Text()),
        sa.Column("metrics", postgresql.JSONB(), nullable=False),
        sa.Column("trades", postgresql.JSONB()),
    )
    op.create_index(
        "ix_backtest_run__created_at_desc", "backtest_run", [sa.text("created_at DESC")]
    )
    op.create_index(
        "uq_backtest_run__tag",
        "backtest_run",
        ["tag"],
        unique=True,
        postgresql_where=sa.text("tag IS NOT NULL"),
    )

    # audit_event
    op.create_table(
        "audit_event",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "ts", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column("actor_type", sa.Text(), nullable=False),
        sa.Column(
            "actor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("account.id", name="fk_audit_event__account"),
            nullable=True,
        ),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.Text(), nullable=False),
        sa.Column("entity_id", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text()),
        sa.Column("ip", sa.Text()),
        sa.Column("user_agent", sa.Text()),
        sa.Column("before", postgresql.JSONB()),
        sa.Column("after", postgresql.JSONB()),
        sa.Column("hash", sa.Text(), nullable=False),
        sa.UniqueConstraint("hash", name="uq_audit_event__hash"),
    )
    op.create_index("ix_audit_event__ts_desc", "audit_event", [sa.text("ts DESC")])
    op.create_index(
        "ix_audit_event__entity_type_entity_id_ts_desc",
        "audit_event",
        ["entity_type", "entity_id", sa.text("ts DESC")],
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION audit_raise_on_change() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'audit_event table is immutable';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION audit_compute_hash() RETURNS trigger AS $$
        BEGIN
            IF NEW.hash IS NULL THEN
                NEW.hash := encode(
                    digest(
                        jsonb_build_object(
                            'ts', NEW.ts,
                            'actor_type', NEW.actor_type,
                            'actor_id', NEW.actor_id,
                            'action', NEW.action,
                            'entity_type', NEW.entity_type,
                            'entity_id', NEW.entity_id,
                            'reason', NEW.reason,
                            'before', NEW.before,
                            'after', NEW.after
                        )::text,
                        'sha256'
                    ),
                    'hex'
                );
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_audit_event_no_change
        BEFORE UPDATE OR DELETE ON audit_event
        FOR EACH ROW EXECUTE FUNCTION audit_raise_on_change();
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_audit_event_compute_hash
        BEFORE INSERT ON audit_event
        FOR EACH ROW EXECUTE FUNCTION audit_compute_hash();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_event_no_change ON audit_event")
    op.execute("DROP TRIGGER IF EXISTS trg_audit_event_compute_hash ON audit_event")
    op.execute("DROP FUNCTION IF EXISTS audit_raise_on_change")
    op.execute("DROP FUNCTION IF EXISTS audit_compute_hash")

    op.drop_index("ix_audit_event__entity_type_entity_id_ts_desc", table_name="audit_event")
    op.drop_index("ix_audit_event__ts_desc", table_name="audit_event")
    op.drop_table("audit_event")

    op.drop_index("uq_backtest_run__tag", table_name="backtest_run")
    op.drop_index("ix_backtest_run__created_at_desc", table_name="backtest_run")
    op.drop_table("backtest_run")

    op.drop_index("uq_alert__dedup_key", table_name="alert")
    op.drop_index("ix_alert__type_ts_desc", table_name="alert")
    op.drop_index("ix_alert__severity_ts_desc", table_name="alert")
    op.drop_index("ix_alert__ts_desc", table_name="alert")
    op.drop_table("alert")

    op.drop_index("ix_pnl_minute__instrument_id_ts", table_name="pnl_minute")
    op.drop_index("ix_pnl_minute__ts", table_name="pnl_minute")
    op.drop_table("pnl_minute")

    op.drop_index("ix_position__trading_day", table_name="position")
    op.drop_index("ix_position__instrument_id", table_name="position")
    op.drop_table("position")

    op.drop_index("uq_execution__trade_id", table_name="execution")
    op.drop_index("ix_execution__ts", table_name="execution")
    op.drop_index("ix_execution__order_id_ts", table_name="execution")
    op.drop_table("execution")

    op.drop_index("uq_order__broker_order_id", table_name="order")
    op.drop_index("ix_order__open", table_name="order")
    op.drop_index("ix_order__instrument_id_status", table_name="order")
    op.drop_index("ix_order__account_id_placed_at_desc", table_name="order")
    op.drop_table("order")

    op.drop_index("ix_signal__ts_desc", table_name="signal")
    op.drop_index("ix_signal__instrument_id_ts_desc", table_name="signal")
    op.drop_table("signal")

    op.drop_index("uq_config__key_active", table_name="config")
    op.drop_index("ix_config__created_at_desc", table_name="config")
    op.drop_table("config")

    op.drop_index("ix_model_artifact__is_active", table_name="model_artifact")
    op.drop_table("model_artifact")

    op.drop_index("ix_instrument__symbol", table_name="instrument")
    op.drop_index("ix_instrument__is_tradable", table_name="instrument")
    op.drop_table("instrument")

    op.drop_index("ix_account__broker", table_name="account")
    op.drop_table("account")

    op.execute("DROP TYPE IF EXISTS alert_severity_enum")
    op.execute("DROP TYPE IF EXISTS liquidity_flag_enum")
    op.execute("DROP TYPE IF EXISTS signal_side_enum")
    op.execute("DROP TYPE IF EXISTS order_status_enum")
    op.execute("DROP TYPE IF EXISTS order_type_enum")
    op.execute("DROP TYPE IF EXISTS order_side_enum")
    op.execute("DROP TYPE IF EXISTS product_enum")
    op.execute("DROP TYPE IF EXISTS exchange_enum")
    op.execute("DROP TYPE IF EXISTS broker_enum")
