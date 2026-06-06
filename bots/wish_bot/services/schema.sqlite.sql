-- SQLite: полная схема для новой БД (data/telegram_bots.db).
-- Применяется один раз при первом запуске. Postgres: schema.sql

CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    invite_code TEXT NOT NULL UNIQUE,
    is_public INTEGER NOT NULL DEFAULT 0,
    admin_id INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    locale TEXT NOT NULL DEFAULT 'ru',
    current_group_id INTEGER REFERENCES groups (id) ON DELETE SET NULL,
    active_menu_chat_id INTEGER,
    active_menu_message_id INTEGER,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fsm_data (
    storage_key TEXT PRIMARY KEY,
    state TEXT,
    data_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS group_members (
    group_id INTEGER NOT NULL REFERENCES groups (id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    joined_at TEXT NOT NULL,
    PRIMARY KEY (group_id, user_id)
);

CREATE TABLE IF NOT EXISTS wishes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL REFERENCES groups (id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    taken_by_id INTEGER,
    taken_at TEXT,
    completed_at TEXT,
    completion_message TEXT,
    deleted INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_wishes_group_status ON wishes (group_id, status);

CREATE TABLE IF NOT EXISTS wish_subscriptions (
    group_id INTEGER NOT NULL REFERENCES groups (id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    subscribed_at TEXT NOT NULL,
    PRIMARY KEY (group_id, user_id)
);

CREATE TABLE IF NOT EXISTS group_blocks (
    group_id INTEGER NOT NULL REFERENCES groups (id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    blocked_at TEXT NOT NULL,
    blocked_by_id INTEGER NOT NULL,
    PRIMARY KEY (group_id, user_id)
);
