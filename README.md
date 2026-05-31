# TelegramBots

Рабочие Telegram-боты (aiogram 3). Один репозиторий, общий `.venv`, запуск через оркестратор `run.py`.

## Общие переменные (все боты)

| Переменная | Описание |
|------------|----------|
| `BOT_MODE` | `polling` (локально) или `webhook` (Cloud Run) — **один режим для всех ботов** |
| `DB_BACKEND` | `sqlite` или `postgres` |
| `SQLITE_PATH` | Путь к файлу SQLite (по умолчанию `data/telegram_bots.db`) |
| `DATABASE_URL` | Postgres (см. `env.example`) |
| `CLOUD_SQL_CONNECTION_NAME` | Альтернатива: `PROJECT:REGION:INSTANCE` + `POSTGRES_*` |
| `WEBHOOK_*`, `PORT` | Настройки webhook (см. `env.example`) |

Схемы БД (новая установка): [`schema.sqlite.sql`](bots/wish_bot/services/schema.sqlite.sql), [`schema.sql`](bots/wish_bot/services/schema.sql) (Postgres).

Инкрементальные миграции: [`db/migrations/`](db/migrations/README.md) (`sqlite/` и `postgres/`).

## Боты

| Папка | Переменная включения | Токен | Описание |
|-------|----------------------|-------|----------|
| `bots/wish_bot` | `WISH_BOT_ENABLED` | `WISH_BOT_TOKEN` | [Бот желаний](bots/wish_bot/README.md) — группы, желания, i18n |

## Первый запуск

```bash
cd ~/TelegramBots
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp env.example .env
# заполните WISH_BOT_TOKEN

python run.py
```

## Docker / Google Cloud

```bash
docker build -t telegram-bots .
docker run --rm --env-file .env -e BOT_MODE=polling telegram-bots
```

Cloud Run: `BOT_MODE=webhook`, `DB_BACKEND=postgres`, `WEBHOOK_URL`, `WISH_BOT_TOKEN`. В **Edit service → Connections** добавить инстанс Cloud SQL. Строка подключения: `postgresql://USER:PASS@/DB?host=/cloudsql/PROJECT:REGION:INSTANCE` (без префикса `DATABASE_URL=` в значении переменной).

## Структура

```
TelegramBots/
├── config/           # общие настройки и create_repository()
├── run.py
├── data/             # SQLite по умолчанию
├── Dockerfile
└── bots/
    └── wish_bot/
```
