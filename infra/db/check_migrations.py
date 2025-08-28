from __future__ import annotations

import os
import subprocess

import psycopg

REQUIRED_TABLES: set[str] = {
    "account",
    "instrument",
    "signal",
    "order",
    "execution",
    "position",
    "pnl_minute",
    "model_artifact",
    "config",
    "alert",
    "backtest_run",
    "audit_event",
}


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    db_url = os.environ["DATABASE_URL"]
    run(["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"])
    with psycopg.connect(db_url.replace("+psycopg", "")) as conn:
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        existing = {row[0] for row in cur.fetchall()}
        missing = REQUIRED_TABLES - existing
        assert not missing, f"missing tables: {missing}"

        cur.execute(
            """
            SELECT constraint_name FROM information_schema.table_constraints
            WHERE table_name='order' AND constraint_type='FOREIGN KEY'
            """
        )
        fks = {row[0] for row in cur.fetchall()}
        assert "fk_order__account" in fks
        assert "fk_order__instrument" in fks

        cur.execute(
            """
            SELECT constraint_name FROM information_schema.table_constraints
            WHERE table_name='order' AND constraint_type='UNIQUE'
            """
        )
        uniques = {row[0] for row in cur.fetchall()}
        assert "uq_order__client_id" in uniques

        cur.execute("SELECT indexname, indexdef FROM pg_indexes WHERE tablename='order'")
        idx = {row[0]: row[1] for row in cur.fetchall()}
        assert (
            "uq_order__broker_order_id" in idx
            and "broker_order_id IS NOT NULL" in idx["uq_order__broker_order_id"]
        )

        cur.execute("SELECT indexname, indexdef FROM pg_indexes WHERE tablename='config'")
        idx_cfg = {row[0]: row[1] for row in cur.fetchall()}
        assert (
            "uq_config__key_active" in idx_cfg and "is_active" in idx_cfg["uq_config__key_active"]
        )

        cur.execute(
            "INSERT INTO audit_event(actor_type, action, entity_type, entity_id) VALUES('system','TEST','x','1') RETURNING id, hash"
        )
        row = cur.fetchone()
        assert row is not None
        audit_id, hash_val = row
        assert hash_val is not None
        try:
            cur.execute("UPDATE audit_event SET reason='oops' WHERE id=%s", (audit_id,))
        except psycopg.errors.RaiseException:
            pass
        else:
            raise AssertionError("audit_event update should fail")
        conn.rollback()

    run(["alembic", "-c", "infra/db/alembic.ini", "downgrade", "base"])
    with psycopg.connect(db_url.replace("+psycopg", "")) as conn:
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        existing = {row[0] for row in cur.fetchall()}
        assert "account" not in existing


if __name__ == "__main__":
    main()
