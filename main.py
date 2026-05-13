import telebot
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread

# 1. ለ Render አስፈላጊ የሆነው Flask አገልግሎት
app = Flask('')

@app.route('/')
def home():
    return "ቦቱ በሰላም እየሰራ ነው!"

def run_app():
    # Render የሚሰጠውን Port በራሱ እንዲያገኝ ያደርጋል
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. የቦት እና የ Gemini ቅንብር
bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
genai.configure(api_key=os.environ.get('GEMINI_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "ይቅርታ፣ አሁን ትንሽ ተጨናንቄያለሁ። ድጋሚ ይሞክሩ።")

# 3. ቦቱን እና ድረ-ገጹን በአንድ ላይ ማስጀመር
if __name__ == "__main__":
    t = Thread(target=run_app)
    t.start()
    bot.infinity_polling()
