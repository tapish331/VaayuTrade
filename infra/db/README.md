# Database Migrations

## Setup

```bash
export DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/vaayutrade
```

## Running migrations

```bash
alembic -c infra/db/alembic.ini upgrade head
alembic -c infra/db/alembic.ini downgrade base
```
