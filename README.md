# TelegramBots

Рабочие Telegram-боты (aiogram 3). Один репозиторий, общий `.venv`, запуск через оркестратор `run.py`.

## Боты

| Папка | Переменная включения | Токен | Описание |
|-------|----------------------|-------|----------|
| `bots/wish_bot` | `WISH_BOT_ENABLED` | `WISH_BOT_TOKEN` | [Бот желаний](bots/wish_bot/README.md) — группы, желания, i18n |

Дополнительно для wish_bot: `WISH_BOT_STORAGE` (`sqlite` | `memory` | `postgres`), `WISH_BOT_SQLITE_PATH`, `DATABASE_URL` (Heroku).

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

## Heroku

- `Procfile`: `worker: python run.py`
- Config Vars: см. `env.example`
- После деплоя: `heroku ps:scale worker=1`
- Python: рекомендуется `.python-version` с `3.12` (см. [документацию Heroku](https://devcenter.heroku.com/articles/python-runtimes))

## Структура

```
TelegramBots/
├── run.py
├── Procfile
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
