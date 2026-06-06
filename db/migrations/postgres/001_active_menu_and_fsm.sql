ALTER TABLE users ADD COLUMN IF NOT EXISTS active_menu_chat_id BIGINT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS active_menu_message_id BIGINT;

CREATE TABLE IF NOT EXISTS fsm_data (
    storage_key TEXT PRIMARY KEY,
    state TEXT,
    data_json JSONB NOT NULL DEFAULT '{}'::jsonb
);
