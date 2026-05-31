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

- `WISH_BOT_STORAGE=sqlite` (по умолчанию) — локальный файл `bots/wish_bot/data/wish_bot.db`, данные сохраняются между перезапусками
- `WISH_BOT_SQLITE_PATH` — свой путь к файлу SQLite (опционально)
- `WISH_BOT_STORAGE=memory` — только RAM, для быстрых тестов
- `WISH_BOT_STORAGE=postgres` + `DATABASE_URL` — для Google Cloud SQL (пока заглушка в `services/postgres_storage.py`, схема в `services/schema.sql`)

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
├── services/       # repository, memory_storage, schema.sql
├── utils/
└── locales/        # ru, en (Fluent)
```

## Ручной тест (2 аккаунта)

1. Аккаунт A: `/create_group` → приватная → скопировать ссылку
2. Аккаунт B: открыть ссылку → `/add_wish` (B) и `/add_wish` (A)
3. A: `/wishes` → «Взять» желание B → проверить «для кого»
4. A: `/my_taken` → «Выполнено» → текст или `/skip`
5. B: проверить DM от бота
