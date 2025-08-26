# VaayuTrade

A disciplined, ML-driven intraday equities bot for Zerodha (Kite Connect) that trades your plan, not your emotions. Streams live ticks, computes online features, scores a calibrated model (LightGBM → ONNX), and executes sliced LIMIT entries with TP / SL-L OCO, strict risk caps, and auto-flat by 15:18 IST. Includes backtester parity, Next.js dashboard, Postgres/Redis, Docker, CI/CD.

## Why this exists
Manual intraday trading is error-prone (late entries, missed exits, emotions, API rejects). VaayuTrade turns signals into auditable, risk-capped execution with dashboards and alerts, ending each day flat.

## Directory layout
```

apps/        # trader daemon, API, dashboard (scaffolds)
packages/    # broker adapter, strategy, backtester, shared libs
infra/       # terraform & github workflows (later tasks)
docs/        # ADRs, runbooks

````

## Getting started (Task 01 baseline)
1) Install git & Python 3.11+ and pre-commit.
2) Clone the repo and enter `VaayuTrade/`.
3) Install hooks:
   ```bash
   pre-commit install
````

4. Sanity “build” (placeholder for Task 01):

   ```bash
   make build
   ```

You should see **OK**. Toolchains, CI, and packages are added in later tasks.

## Notes

* Single user, NSE cash intraday (MIS) only.
* Bracket Orders are not used; OCO logic is implemented in-bot.
* Force-flat before broker auto square-off.

> Full discovery and state machine plans are tracked in `/docs` and issues/PRs.

````
