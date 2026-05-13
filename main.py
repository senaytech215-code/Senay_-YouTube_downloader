import os
import telebot
from flask import Flask, request

# Render Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "ቦቱ በሰላም እየሰራ ነው!"

# ዋናው ማስተካከያ እዚህ ጋር ነው - Path መጠቀሙን እናጥፋው
@app.route('/', methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"የላክኸው መልእክት ደርሶኛል፦ {message.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
