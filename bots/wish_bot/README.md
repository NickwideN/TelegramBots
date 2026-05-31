# wish_bot — Бот желаний

Telegram-бот для групп: участники добавляют желания, видят анонимный список, берут на исполнение и отправляют автору сообщение при выполнении.

## Возможности

- Создание группы (публичной или приватной) с invite-ссылкой
- Вступление по ссылке `https://t.me/BotName?start=join_CODE` или из списка публичных групп
- Добавление желаний, анонимный список открытых
- Взятие желания (исполнителю видно имя и @username автора)
- Завершение с сообщением автору (анонимно; `/skip` — стандартная фраза)
- Подписка на новые желания в группе (`/subscribe`, `/unsubscribe`) — DM с текстом и кнопкой «Взять»
- Локализация: русский и английский

## Локальный запуск

Из корня репозитория `TelegramBots`:

```bash
cp env.example .env
# укажите WISH_BOT_TOKEN в .env

source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

`BOT_MODE=polling` (по умолчанию) — long polling. Для Google Cloud Run: `BOT_MODE=webhook`, `WEBHOOK_URL`, `PORT=8080`, эндпоинты `/health` и `/webhook`.

Только этот бот:

```bash
python -m bots.wish_bot.main
```

## Команды

| Команда | Описание |
|---------|----------|
| `/start` | Справка; `?start=join_CODE` — вступить в группу |
| `/help` | Справка |
| `/language` | Язык (ru / en) |
| `/create_group` | Создать группу |
| `/groups` | Публичные группы |
| `/group` | Текущая группа |
| `/group_admin` | Настройки группы (админ) |
| `/group_members` | Участники и блокировка (админ) |
| `/group_blocked` | Заблокированные и разблокировка (админ) |
| `/add_wish` | Добавить желание |
| `/wishes` | Открытые желания |
| `/my_wishes` | Мои желания (удаление) |
| `/my_taken` | Мои взятые желания |
| `/archive` | Архив выполненных желаний |
| `/subscribe` | Уведомления о новых желаниях в текущей группе |
| `/unsubscribe` | Отключить уведомления |

## Хранилище

Общие переменные в корневом `.env` (см. `env.example`):

- `DB_BACKEND=sqlite` — файл `data/telegram_bots.db` (схема `schema.sqlite.sql` создаётся только при первом запуске)
- `DB_BACKEND=postgres` + `DATABASE_URL` — Cloud SQL (схема: `services/schema.sql`)

Фабрика репозитория: `config/settings.py` → `create_repository()`.

## Структура

```
bots/wish_bot/
├── bootstrap.py    # общая сборка Bot + Dispatcher
├── run_polling.py
├── run_webhook.py
├── main.py         # python -m bots.wish_bot.main → polling
├── config_data/
├── handlers/       # commands, groups, wishes
├── middlewares/    # i18n, group_context
├── states/
├── services/       # repository, sqlite/postgres, schema.*.sql
├── utils/
└── locales/        # ru, en (Fluent)
```

## Ручной тест (2 аккаунта)

1. Аккаунт A: `/create_group` → приватная → скопировать ссылку
2. Аккаунт B: открыть ссылку → `/add_wish` (B) и `/add_wish` (A)
3. A: `/wishes` → «Взять» желание B → проверить «для кого»
4. A: `/my_taken` → «Выполнено» → текст или `/skip`
5. B: проверить DM от бота
