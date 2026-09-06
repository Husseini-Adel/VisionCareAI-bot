import logging
from database.database import create_appointment

logger = logging.getLogger(__name__)

def book_appointment(service_name: str, preferred_date: str, preferred_time: str, chat_id: int, customer_name: str) -> str:
    """تسجيل موعد جديد في SQLite."""
    appt_id = create_appointment(
        chat_id=chat_id,
        customer_name=customer_name,
        service_name=service_name,
        date=preferred_date,
        time=preferred_time
    )
    logger.info(f"Appointment #{appt_id} booked for chat_id={chat_id}")
    return f"تم تأكيد حجزك بنجاح برقم حجز (#{appt_id}) لخدمة ({service_name}) بتاريخ {preferred_date} الساعة {preferred_time}."
