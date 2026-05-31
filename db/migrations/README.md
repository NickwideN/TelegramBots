# Миграции БД

Общая БД для всех ботов (`DB_BACKEND`, `config/settings.py`). Базовая схема для **новых** установок:

| Движок   | Файл |
|----------|------|
| SQLite   | [`bots/wish_bot/services/schema.sqlite.sql`](../../bots/wish_bot/services/schema.sqlite.sql) |
| Postgres | [`bots/wish_bot/services/schema.sql`](../../bots/wish_bot/services/schema.sql) |

При первом запуске SQLite применяется только базовая схема (если БД пустая). Postgres применяет `schema.sql` при каждом старте (`CREATE IF NOT EXISTS`).

## Куда класть новые миграции

```
db/migrations/
├── sqlite/          # 001_description.sql, 002_...
├── postgres/        # те же номера, SQL под PostgreSQL
└── README.md        # этот файл
```

Именование: `NNN_краткое_имя.sql` (например `003_wish_priority.sql`).

Одна и та же **логическая** миграция — два файла, если синтаксис отличается (SQLite vs Postgres). Номер `NNN` должен совпадать.

## Как применять (пока вручную)

1. Написать SQL в `db/migrations/sqlite/` и/или `postgres/`.
2. Локально выполнить против своей БД (sqlite3 / psql / Cloud SQL Studio).
3. На проде — один раз через Cloud SQL или скрипт деплоя.

Таблица учёта (когда появится раннер в коде):

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## Позже (опционально)

- скрипт `scripts/migrate.py`, который читает `db/migrations/{backend}/` и пишет в `schema_migrations`;
- или Alembic с двумя ветками — если миграций станет много.

**Не** добавлять `ALTER` снова в `sqlite_storage._init_db` — только сюда.
