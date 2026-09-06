from telegram.request import HTTPXRequest
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)
import config
from bot.handlers import (
    start_handler,
    release_bot_handler,
    customer_message_handler,
    staff_group_message_handler
)
from services.handoff import set_bot_instance

def create_bot_application():
    request_config = HTTPXRequest(
        connect_timeout=config.TIMEOUT_SECONDS,
        read_timeout=config.TIMEOUT_SECONDS,
        write_timeout=config.TIMEOUT_SECONDS,
        pool_timeout=config.TIMEOUT_SECONDS
    )

    app = (
        ApplicationBuilder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .request(request_config)
        .build()
    )

    set_bot_instance(app)

    # أوامر عامة
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("bot", release_bot_handler))

    # رسائل مجموعة الموظفين (فقط ردود الموظفين داخل المجموعة)
    app.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & filters.REPLY & filters.TEXT,
            staff_group_message_handler
        )
    )

    # رسائل العملاء في الخاص
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND,
            customer_message_handler
        )
    )

    return app