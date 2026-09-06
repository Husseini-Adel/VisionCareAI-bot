import os
import gc
import time
import sqlite3
import config

# استخدام قاعدة اختبار معزولة
config.DATABASE_PATH = "test_visioncare.db"
config.MEMORY_WINDOW = 3

from database.database import (
    init_db,
    upsert_user,
    save_message,
    get_recent_messages,
    create_appointment,
    create_handoff,
    is_user_in_handoff,
    release_user_handoff
)

def safe_remove_file(filepath: str):
    """محاولة حذف الملف بأمان في ويندوز مع تنظيف المقابض"""
    gc.collect()  # تفريغ الذاكرة لإغلاق أي مؤشرات مؤقتة
    if os.path.exists(filepath):
        for _ in range(3):
            try:
                os.remove(filepath)
                break
            except PermissionError:
                time.sleep(0.5)

def run_tests():
    print("=== بدء اختبارات SQLite و Persistent Memory ===")
    
    safe_remove_file("test_visioncare.db")

    # TEST 1: إنشاء قاعدة البيانات تلقائياً
    init_db()
    assert os.path.exists("test_visioncare.db"), "TEST 1 Failed: لم يتم إنشاء الملف."
    print("✔ TEST 1: تم إنشاء قاعدة البيانات بنجاح.")

    # TEST 2 & 6: إضافة المستخدمين واختبار العزل
    upsert_user(1001, "أحمد علي", "ahmed")
    upsert_user(2002, "سارة محمد", "sara")
    upsert_user(1001, "أحمد علي المعدل", "ahmed_new")
    
    conn = sqlite3.connect("test_visioncare.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name, username FROM users WHERE chat_id = 1001")
        user = cursor.fetchone()
        assert user[0] == "أحمد علي المعدل", "فشل تحديث المستخدم"
    finally:
        conn.close()
    print("✔ TEST 2: تم حفظ وتحديث المستخدمين دون تكرار chat_id.")

    # TEST 3 & 4: حفظ المحادثات واختبار MEMORY_WINDOW
    save_message(1001, "user", "مرحبا")
    save_message(1001, "assistant", "أهلاً بك! كيف أساعدك؟")
    save_message(1001, "user", "كم سعر فحص النظر؟")
    save_message(1001, "assistant", "سعر الفحص 5000 ريال.")
    save_message(2002, "user", "أريد شراء نظارة شمسية")

    recent_1001 = get_recent_messages(1001, limit=3)
    assert len(recent_1001) == 3, f"المتوقع 3 رسائل، وصل {len(recent_1001)}"
    assert recent_1001[0]["role"] == "assistant"
    assert recent_1001[1]["role"] == "user"
    assert recent_1001[2]["role"] == "assistant"
    print("✔ TEST 3 & 4: تم حفظ المحادثات وتطبيق MEMORY_WINDOW بنجاح.")

    recent_2002 = get_recent_messages(2002, limit=3)
    assert len(recent_2002) == 1, "حدث تداخل بين بيانات المستخدمين!"
    assert recent_2002[0]["message"] == "أريد شراء نظارة شمسية"
    print("✔ TEST 6: تم التحقق من عزل المستخدمين بنجاح تام.")

    # TEST 7: الحجوزات
    appt_id = create_appointment(1001, "أحمد علي", "فحص النظر الشامل", "2026-09-10", "10:00 AM")
    conn = sqlite3.connect("test_visioncare.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT service_name, status FROM appointments WHERE id = ?", (appt_id,))
        appt = cursor.fetchone()
        assert appt[0] == "فحص النظر الشامل" and appt[1] == "مؤكد"
    finally:
        conn.close()
    print(f"✔ TEST 7: تم إنشاء الحجز بنجاح برقم {appt_id}.")

    # TEST 9: الـ Handoff
    create_handoff(1001, "ألم حاد في العين", "حرجة")
    assert is_user_in_handoff(1001) is True, "فشل تسجيل حالة التحويل"
    release_user_handoff(1001)
    assert is_user_in_handoff(1001) is False, "فشل فك حالة التحويل"
    print("✔ TEST 9: تم التحقق من نظام التحويل البشري ومطابقة الحالات بنجاح.")

    # تنظيف الملف المؤقت بأمان
    safe_remove_file("test_visioncare.db")
    print("=== جميع اختبارات قاعدة البيانات والذاكرة نجحت 100% ===")

if __name__ == "__main__":
    run_tests()