import os
import telebot
from flask import Flask, request
import google.generativeai as genai

# 1. የ Render ምስጢራዊ ቁልፎችን (Tokens) ማንበቢያ
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

# 2. የቴሌግራም እና የ Gemini ዝግጅት (የተስተካከለ ስም)
bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

app = Flask(__name__)

# 3. ቴሌግራም መልእክት ሲልክ የሚቀበለው የዌብሁክ በር
@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'ok', 200
    return 'Gemini Bot Server is Running!', 200

# 4. የ /start command ማስተናገጃ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ሰላም ሰናይ 👋 እኔ የ Gemini AI ቦት ነኝ። የምትፈልገውን ጥያቄ ጠይቀኝ!")

# 5. ዋናው የ Gemini AI ቻት ማስተናገጃ
@bot.message_handler(func=lambda message: True)
def handle_chat(message):
    try:
        user_text = message.text
        # የ Gemini አእምሮ መልስ እንዲያመነጭ ማዘዝ
        response = model.generate_content(user_text)
        bot.reply_to(message, response.text)
    except Exception as e:
        # ለጊዜው ስህተት ካለ በግልጽ እንዲነግረን ማድረጊያ
        bot.reply_to(message, f"❌ ስህተት ተፈጥሯል:\n{str(e)}")
        print(f"Error: {e}")

if __name__ == "__main__":
    # Render የሚፈልገውን ፖርት በትክክል መያዝ
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
