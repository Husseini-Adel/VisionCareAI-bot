import asyncio
import logging
from telegram import Update
from telegram.error import TimedOut, NetworkError
from telegram.ext import ContextTypes
from database.memory import (
    record_user_activity,
    append_user_message,
    append_assistant_message,
    check_handoff_status,
    clear_handoff_status
)
from ai.gemini import ask_gemini

logger = logging.getLogger(__name__)

async def safe_reply(update: Update, text: str, max_retries: int = 3):
    """إرسال آمن يتحمل انقطاع أو بطء الاتصال."""
    for attempt in range(max_retries):
        try:
            await update.message.reply_text(text)
            return
        except (TimedOut, NetworkError) as e:
            logger.warning(f"تأخر الاتصال بتيليجرام (محاولة {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"خطأ غير متوقع في الإرسال: {e}")
            break

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    record_user_activity(
        chat_id=chat_id,
        name=user.full_name or "عميل",
        username=user.username or "لا يوجد"
    )
    clear_handoff_status(chat_id)

    welcome_text = (
        "مرحباً بك في مركز الرؤية الواضحة للبصريات 👓\n"
        "أنا VisionCare AI، كيف أستطيع خدمتك اليوم بخصوص الفحوصات أو النظارات والعدسات؟"
    )
    await safe_reply(update, welcome_text)

async def release_bot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    clear_handoff_status(chat_id)
    await safe_reply(update, "تم تفعيل المساعد الذكي مجدداً. كيف نساعدك الآن؟")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user = update.effective_user
    user_text = update.message.text.strip()
    user_name = user.full_name or "عميل"
    username = user.username or "لا يوجد"

    # تحديث بيانات المستخدم في SQLite
    record_user_activity(chat_id, user_name, username)

    # التحقق من حالة التحويل البشري
    if check_handoff_status(chat_id):
        logger.info(f"User {chat_id} is in handoff mode. Bot skipped auto-reply.")
        return

    # حفظ رسالة المستخدم أولاً في SQLite
    append_user_message(chat_id, user_text)

    # طلب الرد من Gemini (يستعيد السياق تلقائياً من SQLite)
    bot_reply = ask_gemini(
        chat_id=chat_id,
        user_text=user_text,
        user_name=user_name,
        username=username
    )

    # حفظ رد المساعد في SQLite
    append_assistant_message(chat_id, bot_reply)

    # إرسال الرد
    await safe_reply(update, bot_reply)