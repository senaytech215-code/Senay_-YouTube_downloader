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
    return 'Model Lister Server is Running!', 200

# 3. የ /start ማስተናገጃ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ሰላም ሰናይ 👋 አሁን ማንኛውንም ጽሑፍ ጻፍልኝና ያሉትን የ Gemini ሞዴሎች ዝርዝር በሙሉ አወጣልሃለሁ!")

# 4. ዋናው ማስተናገጃ (የጉግልን ሞዴሎች በሙሉ ዘርዝሮ ለቴሌግራም የሚልክ)
@bot.message_handler(func=lambda message: True)
def handle_chat(message):
    try:
        # 🎯 ጉግል ያለውን የሞዴሎች ዝርዝር (ListModels) የምንጠይቅበት ይፋዊ የ API በር
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_KEY}"
        
        response = requests.get(url)
        response_data = response.json()
        
        # ምላሹ በትክክል ከመጣ ዝርዝሩን ማዘጋጀት
        if 'models' in response_data:
            model_list_text = "🎯 **የተገኙ የጉግል AI ሞዴሎች ዝርዝር፦**\n\n"
            
            # የመጀመሪያዎቹን 15 ሞዴሎች ስም ብቻ ቀንጭቦ ለቴሌግራም ማደራጃ
            for index, model in enumerate(response_data['models'][:15], start=1):
                model_name = model.get('name', 'Unknown')
                supported_methods = model.get('supportedGenerationMethods', [])
                
                # generateContent የሚችሉትን ብቻ ለይቶ ለማወቅ ምልክት ማድረግ
                method_status = "✅" if "generateContent" in str(supported_methods) else "❌"
                
                model_list_text += f"{index}. `{model_name}` {method_status}\n"
                
            bot.reply_to(message, model_list_text, parse_mode="Markdown")
        else:
            # ስህተት ካለ ሙሉውን መልእክት ማሳያ
            bot.reply_to(message, f"⚠️ ዝርዝሩን ማግኘት አልተቻለም:\n{str(response_data)}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ በኮዱ ላይ ስህተት ተፈጥሯል:\n{str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
