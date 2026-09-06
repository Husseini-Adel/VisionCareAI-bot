import logging
import config
from database.database import init_db
from bot.telegram import create_bot_application

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    init_db()

    if not config.TELEGRAM_BOT_TOKEN or config.TELEGRAM_BOT_TOKEN == "ضع_توكن_البوت_هنا":
        logger.error("يرجى وضع توكن البوت الحقيقي داخل TELEGRAM_BOT_TOKEN في ملف config.py")
        return

    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "ضع_مفتاح_Gemini_هنا":
        logger.error("يرجى وضع مفتاح Gemini الحقيقي داخل GEMINI_API_KEY في ملف config.py")
        return

    logger.info("Starting VisionCare AI v0.2...")
    app = create_bot_application()
    logger.info("Bot is polling Telegram...")
    app.run_polling()

if __name__ == "__main__":
    main()