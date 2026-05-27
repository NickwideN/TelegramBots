# TelegramBots

Рабочие Telegram-боты (aiogram 3). Один репозиторий, общий `.venv`, запуск через оркестратор `run.py`.

## Боты

| Папка | Переменная включения | Токен |
|-------|----------------------|-------|
| `bots/wish_bot` | `WISH_BOT_ENABLED` | `WISH_BOT_TOKEN` |

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
- Config Vars: те же имена, что в `env.example`
- После деплоя: `heroku ps:scale worker=1`

## Структура

```
TelegramBots/
├── run.py              # оркестратор, asyncio.gather по включённым ботам
├── Procfile
├── requirements.txt
├── env.example
└── bots/
    └── wish_bot/
        ├── main.py
        ├── config_data/
        └── handlers/
```
