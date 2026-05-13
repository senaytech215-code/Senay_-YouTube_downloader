import os
import telebot
from flask import Flask, request

# Token ከ Render Variables ይቀበላል
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return 'ok', 200
    return 'Server is Running', 200

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "አሁን በይፋ ተገናኝተናል!")

if __name__ == "__main__":
    # Render የሚፈልገውን ፖርት በትክክል ለመያዝ
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
