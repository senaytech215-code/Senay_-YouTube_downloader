import os
import telebot
import requests
import time  # 🎯 የሰከንድ ማረፊያ ለመጨመር
from flask import Flask, request

BOT_TOKEN = os.environ.get('BOT_TOKEN')

GEMINI_KEYS = [
    os.environ.get('GEMINI_KEY'),
    os.environ.get('GEMINI_KEY_2'),
    os.environ.get('GEMINI_KEY_3')
]
GEMINI_KEYS = [key for key in GEMINI_KEYS if key]

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'ok', 200
    return 'Gemini Protected Multi-Key Server is Running!', 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ሰላም ሰናይ 👋 ቦቱ በሰከንድ መተንፈሻ ጥበቃ ታድሷል። የምትፈልገውን ጠይቀኝ!")

def ask_gemini(user_text):
    payload = {"contents": [{"parts": [{"text": user_text}]}]}
    headers = {'Content-Type': 'application/json'}
    
    for index, key in enumerate(GEMINI_KEYS):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response_data = response.json()
            
            if 'error' in response_data:
                error_code = response_data['error'].get('code')
                print(f"Key {index+1} failed with error code: {error_code}")
                
                if error_code in [429, 503]:
                    # 🎯 ዋናው ማስተካከያ፦ ወደ ቀጣዩ ቁልፍ ከመሄዱ በፊት 2 ሰከንድ ሰርቨሩ እንዲያርፍ ማድረግ
                    time.sleep(2)
                    continue
                else:
                    return f"✖️ ከጉግል ሲስተም ስህተት ተመልሷል: {response_data['error'].get('message')}"
            
            if 'candidates' in response_data:
                return response_data['candidates'][0]['content']['parts'][0]['text']
                
        except Exception as e:
            print(f"Exception on key {index+1}: {str(e)}")
            time.sleep(2) # ስህተት ሲመጣ ማረፍ
            continue
            
    return "⏳ ይቅርታ ሰናይ፣ በአሁኑ ሰዓት የጉግል ሲስተም በጣም ተጨናንቋል። እባክዎ ከ30 ሰከንድ በኋላ መልሰው ይሞክሩ።"

@bot.message_handler(func=lambda message: True)
def handle_chat(message):
    status_message = None
    try:
        user_text = message.text
        status_message = bot.reply_to(message, "🤔 በማሰብ ላይ...")
        ai_reply = ask_gemini(user_text)
        bot.edit_message_text(ai_reply, chat_id=message.chat.id, message_id=status_message.message_id)
            
    except Exception as e:
        if status_message:
            bot.edit_message_text(f"❌ በቦቱ ላይ ስህተት ተፈጥሯል:\n{str(e)}", chat_id=message.chat.id, message_id=status_message.message_id)
        else:
            bot.reply_to(message, f"❌ በቦቱ ላይ ስህተት ተፈጥሯል:\n{str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
