# TelegramBots

Рабочие Telegram-боты (aiogram 3). Один репозиторий, общий `.venv`, запуск через оркестратор `run.py`.

## Боты

| Папка | Переменная включения | Токен | Описание |
|-------|----------------------|-------|----------|
| `bots/wish_bot` | `WISH_BOT_ENABLED` | `WISH_BOT_TOKEN` | [Бот желаний](bots/wish_bot/README.md) — группы, желания, i18n |

Дополнительно для wish_bot: `WISH_BOT_STORAGE` (`sqlite` | `memory` | `postgres`), `WISH_BOT_SQLITE_PATH`, `DATABASE_URL` (Cloud SQL).

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

Сборка и локальный запуск образа:

```bash
docker build -t telegram-bots .
docker run --rm --env-file .env telegram-bots
```

Переменные окружения задаются в Cloud Run (см. `env.example`), не кладите `.env` в образ.

## Структура

```
TelegramBots/
├── run.py
├── Dockerfile
├── requirements.txt
├── env.example
└── bots/
    └── wish_bot/
        ├── main.py
        ├── handlers/
        ├── services/
        ├── locales/
        └── ...
```
