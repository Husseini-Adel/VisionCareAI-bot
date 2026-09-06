import sqlite3
import logging
import config

logger = logging.getLogger(__name__)

def get_connection():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """إنشاء الجداول وعمل Migration آمن للأعمدة الجديدة"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER UNIQUE NOT NULL,
            name TEXT,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            customer_name TEXT,
            service_name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'مؤكد',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS handoffs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            urgency TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            staff_group_message_id INTEGER,
            assigned_staff_id INTEGER,
            assigned_staff_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP
        );
        """)

        # فحص وإضافة الأعمدة الجديدة إذا كانت القاعدة موجودة مسبقاً
        cursor.execute("PRAGMA table_info(handoffs);")
        columns = [col["name"] for col in cursor.fetchall()]
        
        if "staff_group_message_id" not in columns:
            cursor.execute("ALTER TABLE handoffs ADD COLUMN staff_group_message_id INTEGER;")
        if "assigned_staff_id" not in columns:
            cursor.execute("ALTER TABLE handoffs ADD COLUMN assigned_staff_id INTEGER;")
        if "assigned_staff_name" not in columns:
            cursor.execute("ALTER TABLE handoffs ADD COLUMN assigned_staff_name TEXT;")

        conn.commit()
        logger.info(f"Database initialized and schema verified at '{config.DATABASE_PATH}'.")
    finally:
        conn.close()

def upsert_user(chat_id: int, name: str, username: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO users (chat_id, name, username, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(chat_id) DO UPDATE SET
            name = excluded.name,
            username = excluded.username,
            updated_at = CURRENT_TIMESTAMP;
        """, (chat_id, name, username))
        conn.commit()
    finally:
        conn.close()

def save_message(chat_id: int, role: str, message: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO conversations (chat_id, role, message)
        VALUES (?, ?, ?);
        """, (chat_id, role, message))
        conn.commit()
    finally:
        conn.close()

def get_recent_messages(chat_id: int, limit: int = None) -> list:
    if limit is None:
        limit = config.MEMORY_WINDOW
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT role, message FROM (
            SELECT id, role, message FROM conversations
            WHERE chat_id = ?
            ORDER BY id DESC
            LIMIT ?
        ) ORDER BY id ASC;
        """, (chat_id, limit))
        rows = cursor.fetchall()
        return [{"role": r["role"], "message": r["message"]} for r in rows]
    finally:
        conn.close()

def create_appointment(chat_id: int, customer_name: str, service_name: str, date: str, time: str) -> int:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO appointments (chat_id, customer_name, service_name, date, time)
        VALUES (?, ?, ?, ?, ?);
        """, (chat_id, customer_name, service_name, date, time))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def create_handoff(chat_id: int, reason: str, urgency: str) -> int:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO handoffs (chat_id, reason, urgency, status)
        VALUES (?, ?, ?, 'pending');
        """, (chat_id, reason, urgency))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def set_handoff_message_id(handoff_id: int, message_id: int):
    """ربط رقم رسالة المجموعة بطلب التحويل"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE handoffs
        SET staff_group_message_id = ?
        WHERE id = ?;
        """, (message_id, handoff_id))
        conn.commit()
    finally:
        conn.close()

def get_handoff_by_staff_message_id(message_id: int):
    """جلب بيانات العميل والطلب عبر رسالة المجموعة التي تم الرد عليها"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM handoffs
        WHERE staff_group_message_id = ? AND status = 'pending'
        ORDER BY id DESC LIMIT 1;
        """, (message_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_active_handoff_by_chat_id(chat_id: int):
    """جلب الطلب النشط لعميل معين"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM handoffs
        WHERE chat_id = ? AND status = 'pending'
        ORDER BY id DESC LIMIT 1;
        """, (chat_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def is_user_in_handoff(chat_id: int) -> bool:
    return get_active_handoff_by_chat_id(chat_id) is not None

def release_user_handoff(chat_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE handoffs
        SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP
        WHERE chat_id = ? AND status = 'pending';
        """, (chat_id,))
        conn.commit()
    finally:
        conn.close()

def resolve_handoff_by_id(handoff_id: int, staff_id: int = None, staff_name: str = None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE handoffs
        SET status = 'resolved',
            assigned_staff_id = ?,
            assigned_staff_name = ?,
            resolved_at = CURRENT_TIMESTAMP
        WHERE id = ?;
        """, (staff_id, staff_name, handoff_id))
        conn.commit()
    finally:
        conn.close()