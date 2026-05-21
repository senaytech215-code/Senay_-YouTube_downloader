import os
import telebot
import requests
from flask import Flask, request

# 1. የ Render ምስጢራዊ ቁልፎችን ማንበቢያ
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# 2. የዌብሁክ በር
@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'ok', 200
    return 'Gemini 2.5 Flash Server is Running!', 200

# 3. የ /start ማስተናገጃ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ሰላም ሰናይ 👋 አሁን በታላቁ Gemini 2.5 Flash ሞዴል ሙሉ በሙሉ ዝግጁ ሆኛለሁ! የምትፈልገውን ጥያቄ ጠይቀኝ።")

# 4. ዋናው የቻት ማስተናገጃ (ወደ አዲሱ gemini-2.5-flash የተመራ)
@bot.message_handler(func=lambda message: True)
def handle_chat(message):
    try:
        user_text = message.text
        
        # 🎯 በጉግል ዝርዝር መሠረት ትክክለኛው የ API መጥሪያ መስመር
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": user_text}]
            }]
        }
        
        # ወደ ጉግል ጥያቄውን መላክ
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        # መልሱን ፈልቅቆ ማውጣት
        if 'candidates' in response_data:
            ai_reply = response_data['candidates'][0]['content']['parts'][0]['text']
            bot.reply_to(message, ai_reply)
        else:
            bot.reply_to(message, f"⚠️ ጉግል ምላሽ አልሰጠም:\n{str(response_data)}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ ስህተት ተፈጥሯል:\n{str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
