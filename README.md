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

По умолчанию `BOT_MODE=polling`. Для Cloud Run — `BOT_MODE=webhook` и `WEBHOOK_URL` (см. `env.example`).

## Docker / Google Cloud

Сборка и локальный запуск образа:

```bash
docker build -t telegram-bots .
# локально с polling (как на машине):
docker run --rm --env-file .env -e BOT_MODE=polling telegram-bots
# как на Cloud Run (нужны WEBHOOK_URL и доступный URL для Telegram):
docker run --rm --env-file .env -e BOT_MODE=webhook -p 8080:8080 telegram-bots
```

В Cloud Run задайте переменные: `BOT_MODE=webhook`, `WEBHOOK_URL=https://ваш-сервис.run.app`, `WEBHOOK_SECRET`, `WISH_BOT_TOKEN`, `PORT=8080`. После первого деплоя проверьте `GET /health` и `getWebhookInfo`.

Переменные окружения задаются в Cloud Run, не кладите `.env` в образ.

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
