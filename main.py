import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get('BOT_TOKEN')

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"ሰላም ሰናይ! ቦቱ አሁን ነቅቷል። የላክኸው መልእክት፦ {user_text}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply))
    print("ቦቱ እየሰራ ነው...")
    app.run_polling() 
