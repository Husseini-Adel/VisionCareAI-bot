from telegram.request import HTTPXRequest
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)
import config
from bot.handlers import start_handler, release_bot_handler, message_handler
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

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("bot", release_bot_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    return app