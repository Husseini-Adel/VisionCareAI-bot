from database.database import (
    upsert_user,
    save_message,
    get_recent_messages,
    is_user_in_handoff,
    release_user_handoff
)

def record_user_activity(chat_id: int, name: str, username: str):
    upsert_user(chat_id, name, username)

def append_user_message(chat_id: int, text: str):
    save_message(chat_id, "user", text)

def append_assistant_message(chat_id: int, text: str):
    save_message(chat_id, "assistant", text)

def fetch_conversation_history(chat_id: int, limit: int = None) -> list:
    return get_recent_messages(chat_id, limit)

def check_handoff_status(chat_id: int) -> bool:
    return is_user_in_handoff(chat_id)

def clear_handoff_status(chat_id: int):
    release_user_handoff(chat_id)