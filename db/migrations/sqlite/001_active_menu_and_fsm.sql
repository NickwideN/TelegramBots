ALTER TABLE users ADD COLUMN active_menu_chat_id INTEGER;
ALTER TABLE users ADD COLUMN active_menu_message_id INTEGER;

CREATE TABLE IF NOT EXISTS fsm_data (
    storage_key TEXT PRIMARY KEY,
    state TEXT,
    data_json TEXT NOT NULL DEFAULT '{}'
);
