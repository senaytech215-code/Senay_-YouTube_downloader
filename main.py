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
    return 'Gemini Stable Server is Running!', 200

# 3. የ /start ማስተናገጃ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ሰላም ሰናይ 👋 እኔ በተረጋጋው Gemini 2.5 Flash የምሰራው ፈጣን ቦት ነኝ። የምትፈልገውን ጠይቀኝ!")

# 4. ዋናው የቻት ማስተናገጃ (በማሰብ ላይ ብሎ መልስ የሚያድስ)
@bot.message_handler(func=lambda message: True)
def handle_chat(message):
    try:
        user_text = message.text
        
        # 🎯 ተጠቃሚው እንዳይሰለች ወዲያውኑ "በማሰብ ላይ..." የሚል መልእክት መላክ
        status_message = bot.reply_to(message, "🤔 በማሰብ ላይ... እባክዎ ጥቂት ሰከንዶች ይጠብቁ")
        
        # ወደ Gemini 2.5 Flash መደበኛ የ API መስመር
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": user_text}]
            }]
        }
        
        # ለጉግል ጥያቄውን መላክ
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        # ከጉግል የመጣውን ምላሽ ፈልቅቆ ማውጣት
        if 'candidates' in response_data:
            ai_reply = response_data['candidates'][0]['content']['parts'][0]['text']
            
            # 🎯 ያንን "በማሰብ ላይ..." የሚለውን መልእክት በ AIው እውነተኛ መልስ መተካት (Edit ማድረግ)
            bot.edit_message_text(ai_reply, chat_id=message.chat.id, message_id=status_message.message_id)
        else:
            bot.edit_message_text(f"⚠️ ጉግል ምላሽ አልሰጠም:\n{str(response_data)}", chat_id=message.chat.id, message_id=status_message.message_id)
            
    except Exception as e:
        bot.reply_to(message, f"❌ ስህተት ተፈጥሯል:\n{str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
