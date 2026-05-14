import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Environment Variables - የዚህን ስም በ Render ላይም እንዳለህ አረጋግጥ!
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

def start(update, context):
    """Handles the /start command."""
    update.message.reply_text('ሰላም! እኔ የምሰራ ቦት ነኝ።')

def echo(update, context):
    """Echoes the user's message back to them."""
    update.message.reply_text(update.message.text)

def main():
    """Starts the bot."""
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN is not set in environment variables.")
        return

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Command Handlers
    dispatcher.add_handler(CommandHandler("start", start))

    # Message Handler (for echoing all other messages)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()
    print("Bot started polling...")
    updater.idle()

# ይህ በጣም አስፈላጊ ነው! በትክክል __name__ እና __main__ ብለህ መጻፍ አለብህ።
if __name__ == '__main__':
    main()
