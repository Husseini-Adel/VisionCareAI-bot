import logging
from google import genai
from google.genai import types
import config
from ai.prompts import SYSTEM_INSTRUCTION
from database.memory import fetch_conversation_history
from services.handoff import transfer_to_human_staff
from services.booking import book_appointment

logger = logging.getLogger(__name__)

# تهيئة آمنة لعميل Gemini
_client = None

def get_client():
    global _client
    if _client is None:
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY غير موجود داخل ملف config.py")
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client

def ask_gemini(chat_id: int, user_text: str, user_name: str, username: str) -> str:
    client = get_client()

    # أدوات العميل المعزولة
    def handle_transfer(reason: str, urgency: str) -> str:
        """تحويل المحادثة إلى موظف بشري فوراً"""
        return transfer_to_human_staff(
            reason=reason,
            urgency=urgency,
            chat_id=chat_id,
            user_name=user_name,
            username=username
        )

    def handle_booking(service_name: str, preferred_date: str, preferred_time: str) -> str:
        """تسجيل حجز موعد جديد في المركز"""
        return book_appointment(
            service_name=service_name,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            chat_id=chat_id,
            customer_name=user_name
        )

    # جلب السياق السابق من SQLite
    history_records = fetch_conversation_history(chat_id, limit=config.MEMORY_WINDOW)
    chat_history_contents = []

    for item in history_records:
        role = "user" if item["role"] == "user" else "model"
        chat_history_contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=item["message"])]
            )
        )

    try:
        chat = client.chats.create(
            model="gemini-3.6-flash",
            history=chat_history_contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.2,
                tools=[handle_transfer, handle_booking]
            )
        )

        response = chat.send_message(user_text)
        return response.text or "تم استلام طلبك ومتابعته بنجاح."

    except Exception as e:
        logger.error(f"Gemini API Error for chat_id {chat_id}: {e}", exc_info=True)
        return "عذراً، حدث خطأ مؤقت أثناء معالجة طلبك. يرجى المحاولة مرة أخرى لاحقاً."