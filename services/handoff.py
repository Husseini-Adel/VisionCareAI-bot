import asyncio
import logging
from telegram.error import TelegramError
from database.database import create_handoff
import config

logger = logging.getLogger(__name__)
bot_app_instance = None

def set_bot_instance(app):
    global bot_app_instance
    bot_app_instance = app

async def _send_staff_notification(alert_message: str):
    """إرسال تنبيه إلى الموظف مع معالجة آمنة للأخطاء"""
    try:
        await bot_app_instance.bot.send_message(
            chat_id=config.STAFF_USER_ID,
            text=alert_message,
            parse_mode="Markdown"
        )
        logger.info(f"Notification delivered to staff ID ({config.STAFF_USER_ID}).")
    except TelegramError as e:
        logger.warning(
            f"تعذر إرسال التنبيه إلى الموظف ({config.STAFF_USER_ID}): {e}. "
            f"تأكد أن الموظف قام بالضغط على /start في بوت تيليجرام أولاً."
        )
    except Exception as e:
        logger.error(f"Unexpected error in staff notification: {e}")

def transfer_to_human_staff(reason: str, urgency: str, chat_id: int, user_name: str, username: str) -> str:
    """تسجيل التحويل في SQLite وإرسال إشعار للموظف."""
    handoff_id = create_handoff(chat_id, reason, urgency)

    client_link = f"tg://user?id={chat_id}" if not username or username == "لا يوجد" else f"https://t.me/{username}"
    alert_message = (
        f"🚨 **تنبيه تحويل عميل (Human Handoff #{handoff_id})**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **العميل:** [{user_name}]({client_link})\n"
        f"🆔 **المعرف:** `{chat_id}`\n"
        f"⚠️ **الأولوية:** {urgency}\n"
        f"📌 **السبب:** {reason}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"يرجى الضغط على اسم العميل أعلاه وبدء متابعته."
    )

    if bot_app_instance and config.STAFF_USER_ID:
        asyncio.create_task(_send_staff_notification(alert_message))

    return "تم إشعار موظف خدمة العملاء بنجاح، وسيتابع معك الآن مباشرة."