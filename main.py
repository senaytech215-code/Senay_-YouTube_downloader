import os
import telebot
from flask import Flask, request

# Render ላይ ያስገባኸውን Token እዚህ ጋር ይቀበላል
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "ቦቱ አሁን በቀላሉ እየሰራ ነው!"

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# የላክነውን መልእክት መልሶ እንዲልክልን (Echo)
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"የላክኸው መልእክት፦ {message.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
