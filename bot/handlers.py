import asyncio
import logging
from telegram import Update
from telegram.error import TimedOut, NetworkError, TelegramError
from telegram.ext import ContextTypes
from database.memory import (
    record_user_activity,
    append_user_message,
    append_assistant_message,
    check_handoff_status,
    clear_handoff_status
)
from database.database import (
    get_handoff_by_staff_message_id,
    get_active_handoff_by_chat_id,
    set_handoff_message_id,
    resolve_handoff_by_id
)
from ai.gemini import ask_gemini
import config

logger = logging.getLogger(__name__)

async def safe_reply(update: Update, text: str, max_retries: int = 3):
    """إرسال رد آمن ومحمي من انقطاع الشبكة"""
    for attempt in range(max_retries):
        try:
            await update.message.reply_text(text)
            return
        except (TimedOut, NetworkError) as e:
            logger.warning(f"Network timeout ({attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
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
    """إعادة تشغيل الذكاء الاصطناعي وإلغاء التحويل"""
    chat_id = update.effective_chat.id
    clear_handoff_status(chat_id)
    await safe_reply(update, "تم تفعيل الرد الآلي عبر المساعد الذكي مجدداً. كيف يمكنني مساعدتك الآن؟")

async def staff_group_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة ردود الموظفين داخل مجموعة Staff Group وتحويلها إلى العميل"""
    message = update.message
    if not message or not message.reply_to_message:
        return

    replied_msg_id = message.reply_to_message.message_id
    staff_reply_text = message.text

    # البحث عن العميل المرتبط بالرسالة التي تم الرد عليها
    handoff = get_handoff_by_staff_message_id(replied_msg_id)
    if not handoff:
        return  # الرد ليس على تذكرة عميل نشطة

    customer_chat_id = handoff["chat_id"]
    handoff_id = handoff["id"]
    staff_name = update.effective_user.full_name

    # إذا كتب الموظف أمر إغلاق التذكرة
    if staff_reply_text.strip() == "/resolve":
        resolve_handoff_by_id(
            handoff_id=handoff_id,
            staff_id=update.effective_user.id,
            staff_name=staff_name
        )
        await message.reply_text(f"✅ تم إغلاق الطلب #{handoff_id} وإعادة العميل للمساعد الذكي.")
        try:
            await context.bot.send_message(
                chat_id=customer_chat_id,
                text="شكراً لتواصلك معنا! تم إنهاء المحادثة مع الموظف وإعادة تفعيل المساعد الذكي. كيف نخدمك؟"
            )
        except TelegramError:
            pass
        return

    # إرسال رسالة الموظف إلى شات العميل
    try:
        await context.bot.send_message(
            chat_id=customer_chat_id,
            text=f"👨‍💼 **موظف خدمة العملاء:**\n{staff_reply_text}"
        )
        # حفظ الرسالة في سجل المحادثات
        append_assistant_message(customer_chat_id, f"[الموظف {staff_name}]: {staff_reply_text}")
        await message.reply_text("✅ تم إيصال ردك إلى العميل.")
    except TelegramError as e:
        await message.reply_text(f"⚠️ فشل إرسال الرد إلى العميل: {e}")

async def customer_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة رسائل العملاء في الشات الخاص"""
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user = update.effective_user
    user_text = update.message.text.strip()
    user_name = user.full_name or "عميل"
    username = user.username or "لا يوجد"

    # تحديث بيانات المستخدم
    record_user_activity(chat_id, user_name, username)

    # 1. إذا كان العميل في وضع التحويل البشري: تمرير رسالته فوراً للمجموعة
    active_handoff = get_active_handoff_by_chat_id(chat_id)
    if active_handoff:
        handoff_id = active_handoff["id"]
        logger.info(f"Forwarding customer message ({chat_id}) to Staff Group for Handoff #{handoff_id}")

        forward_text = (
            f"📩 **رسالة جديدة من العميل في طلب #{handoff_id}:**\n"
            f"👤 {user_name} (`{chat_id}`)\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"{user_text}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"💬 اضغط Reply على هذه الرسالة للرد عليه."
        )

        try:
            sent_msg = await context.bot.send_message(
                chat_id=config.STAFF_GROUP_ID,
                text=forward_text
            )
            # تحديث معرّف الرسالة لكي يستطيع الموظف الرد على أحدث رسالة للعميل
            set_handoff_message_id(handoff_id, sent_msg.message_id)
        except TelegramError as e:
            logger.error(f"Error forwarding message to staff group: {e}")

        await safe_reply(update, "⏳ تم إيصال رسالتك إلى الموظف المختص وجارٍ الرد عليك.")
        return

    # 2. إذا لم يكن محولاً: الرد الطبيعي عبر Gemini الذكي
    append_user_message(chat_id, user_text)

    bot_reply = ask_gemini(
        chat_id=chat_id,
        user_text=user_text,
        user_name=user_name,
        username=username
    )

    append_assistant_message(chat_id, bot_reply)
    await safe_reply(update, bot_reply)