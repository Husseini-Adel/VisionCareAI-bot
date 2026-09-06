import asyncio
import logging
from telegram.error import TelegramError
from database.database import (
    create_handoff,
    set_handoff_message_id,
    get_active_handoff_by_chat_id
)
import config

logger = logging.getLogger(__name__)
bot_app_instance = None

def set_bot_instance(app):
    global bot_app_instance
    bot_app_instance = app

async def _notify_staff_group(handoff_id: int, alert_message: str):
    """إرسال التنبيه إلى مجموعة الموظفين وحفظ معرّف الرسالة للرد عليها"""
    if not bot_app_instance:
        logger.error("bot_app_instance is not set.")
        return

    if not config.STAFF_GROUP_ID:
        logger.warning("STAFF_GROUP_ID is not configured.")
        return

    try:
        sent_msg = await bot_app_instance.bot.send_message(
            chat_id=config.STAFF_GROUP_ID,
            text=alert_message,
            parse_mode="Markdown"
        )
        # حفظ رقم الرسالة للربط اللاحق بالـ Reply
        set_handoff_message_id(handoff_id, sent_msg.message_id)
        logger.info(f"Handoff #{handoff_id} sent to Staff Group. Message ID: {sent_msg.message_id}")
    except TelegramError as e:
        logger.error(f"فشل إرسال التنبيه إلى مجموعة الموظفين: {e}. تأكد أن البوت عضو ومشرف في المجموعة.")

def transfer_to_human_staff(reason: str, urgency: str, chat_id: int, user_name: str, username: str) -> str:
    """استدعاء أداة التحويل وتسجيل الطلب في قاعدة البيانات"""
    handoff_id = create_handoff(chat_id, reason, urgency)

    client_link = f"tg://user?id={chat_id}" if not username or username == "لا يوجد" else f"https://t.me/{username}"
    alert_message = (
        f"🚨 **طلب تحويل عميل جديد (#{handoff_id})**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **العميل:** [{user_name}]({client_link})\n"
        f"🆔 **معرّف العميل:** `{chat_id}`\n"
        f"⚠️ **درجة الأولوية:** {urgency}\n"
        f"📌 **السبب:** {reason}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💬 **للرد على هذا العميل:** اضغط مباشرة على خيار (Reply/رد) على هذه الرسالة واكتب ردك."
    )

    asyncio.create_task(_notify_staff_group(handoff_id, alert_message))

    return "تم إشعار موظف خدمة العملاء بنجاح وسيتابع معك الآن مباشرة."