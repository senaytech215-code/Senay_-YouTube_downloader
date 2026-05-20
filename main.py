import os
import telebot
import requests
import json
import time
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
    return 'Gemini Streaming Server is Running!', 200

# 3. የ /start ማስተናገጃ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ሰላም ሰናይ 👋 እኔ በፈጣኑ Gemini 2.5 Flash Streaming የሚሰራው ቦት ነኝ። የምትፈልገውን ጠይቀኝ!")

# 4. ዋናው የቻት ማስተናገጃ (ቃል በቃል እየጻፈ የሚያድስ)
@bot.message_handler(func=lambda message: True)
def handle_chat(message):
    try:
        user_text = message.text
        
        # 🎯 መጀመሪያ ለተጠቃሚው ፈጣን ምላሽ በመስጠት "በማሰብ ላይ..." የሚል መልእክት መላክ
        status_message = bot.reply_to(message, "🤔 በማሰብ ላይ...")
        
        # ወደ Gemini 2.5 Flash በ Streaming (streamGenerateContent) መጥሪያ ሊንክ
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?key={GEMINI_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": user_text}]
            }]
        }
        
        # ለጉግል ጥያቄውን በ Stream መልክ መላክ
        response = requests.post(url, headers=headers, json=payload, stream=True)
        
        full_reply = ""
        last_update_time = time.time()
        
        # ከጉግል የሚመጡትን ቃላት አንድ በአንድ እያነበቡ መሰብሰብ
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                # የጉግል ስትሪም ዳታ የሚጀምረው በ "data: " ስለሆነ እሱን ማንሳት
                if decoded_line.startswith("data: "):
                    json_str = decoded_line[6:]
                    try:
                        chunk_data = json.loads(json_str)
                        if 'candidates' in chunk_data:
                            chunk_text = chunk_data['candidates'][0]['content']['parts'][0]['text']
                            full_reply += chunk_text
                            
                            # በየ 1.5 ሰከንዱ ቴሌግራም ላይ ያለውን ጽሑፍ ማደስ (ቴሌግራም እንዳይጨናነቅ)
                            if time.time() - last_update_time > 1.5 and full_reply.strip():
                                try:
                                    bot.edit_message_text(full_reply + " ✍️...", chat_id=message.chat.id, message_id=status_message.message_id)
                                    last_update_time = time.time()
                                except Exception:
                                    pass # ተመሳሳይ ጽሑፍ ከሆነ ስህተት እንዳይሰጠን ማለፍ
                    except Exception:
                        continue

        # 🎯 ፍጻሜ፦ ሙሉው ጽሑፍ አልቆ ሲያበቃ "✍️..." የሚለውን ምልክት አንስቶ የመጨረሻውን ጽሑፍ ማቅረብ
        if full_reply.strip():
            bot.edit_message_text(full_reply, chat_id=message.chat.id, message_id=status_message.message_id)
        else:
            bot.edit_message_text("⚠️ ይቅርታ፣ ምንም ምላሽ ማመንጨት አልቻልኩም።", chat_id=message.chat.id, message_id=status_message.message_id)
            
    except Exception as e:
        bot.reply_to(message, f"❌ ስህተት ተፈጥሯል:\n{str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
