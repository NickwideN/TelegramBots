# wish_bot — Бот желаний

## Локальный запуск

Из корня репозитория `TelegramBots`:

```bash
cp env.example .env
# укажите WISH_BOT_TOKEN в .env

source .venv/bin/activate
python run.py
```

Только этот бот (без оркестратора):

```bash
python -m bots.wish_bot.main
```
