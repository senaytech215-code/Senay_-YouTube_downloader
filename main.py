import os
import telebot
from flask import Flask, request

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ይህ ክፍል ቴሌግራም መልእክት ሲልክ የሚቀበለው ነው
@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return 'ok', 200
    return 'Server is Running', 200

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "አሁን ሰርቷል! መልእክትህ ደርሶኛል።")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
