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
    return 'Gemini Protected Server is Running!', 200

# 3. የ /start ማስተናገጃ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ሰላም ሰናይ 👋 እኔ በታላቁ Gemini 2.5 Flash የምሰራው ዘመናዊ ቦት ነኝ። የምትፈልገውን ጠይቀኝ!")

# 4. ዋናው የቻት ማስተናገጃ (ከስህተት መከላከያ ጋር)
@bot.message_handler(func=lambda message: True)
def handle_chat(message):
    status_message = None
    try:
        user_text = message.text
        
        # ወዲያውኑ "በማሰብ ላይ..." የሚል መልእክት መላክ
        status_message = bot.reply_to(message, "🤔 በማሰብ ላይ...")
        
        # 🎯 ወደ ዋናው እና ክፍቱ gemini-2.5-flash የሚወስድ ሊንክ
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
        
        # 1. የኮታ ማለቅ (429) ወይም የመጨናነቅ (503) ስህተት ከመጣ መያዝ
        if 'error' in response_data:
            error_code = response_data['error'].get('code')
            if error_code == 429:
                bot.edit_message_text("⚠️ ይቅርታ ሰናይ፣ በአሁኑ ሰዓት የጉግል ነፃ የጥያቄ ገደብ (Rate Limit) አልፏል። እባክዎ ከ1 ደቂቃ በኋላ እንደገና ይሞክሩ።", chat_id=message.chat.id, message_id=status_message.message_id)
            elif error_code == 503:
                bot.edit_message_text("⏳ ጉግል በአሁኑ ሰዓት በሰዎች ተጨናንቋል። እባክዎ ጥቂት ሰከንዶች ቆይተው ይሞክሩ።", chat_id=message.chat.id, message_id=status_message.message_id)
            else:
                bot.edit_message_text(f"✖️ ከጉግል ሲስተም ስህተት ተመልሷል:\n{response_data['error'].get('message')}", chat_id=message.chat.id, message_id=status_message.message_id)
            return

        # 2. መልሱ በትክክል ከመጣ ማቅረብ
        if 'candidates' in response_data:
            ai_reply = response_data['candidates'][0]['content']['parts'][0]['text']
            bot.edit_message_text(ai_reply, chat_id=message.chat.id, message_id=status_message.message_id)
        else:
            bot.edit_message_text("⚠️ ይቅርታ፣ ያልታወቀ ስህተት አጋጥሟል።", chat_id=message.chat.id, message_id=status_message.message_id)
            
    except Exception as e:
        if status_message:
            bot.edit_message_text(f"❌ በቦቱ ላይ ስህተት ተፈጥሯል:\n{str(e)}", chat_id=message.chat.id, message_id=status_message.message_id)
        else:
            bot.reply_to(message, f"❌ በቦቱ ላይ ስህተት ተፈጥሯል:\n{str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
