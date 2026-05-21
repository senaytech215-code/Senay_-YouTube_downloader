import os
import telebot
import requests
import time
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

user_memory = {}       
user_gender = {}       
user_last_time = {}    

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'ok', 200
    return 'Senay Tech Blue Styled Server is Running!', 200

# 🎯 የ /start ትዕዛዝ - ስም እና Senay Tech ሰማያዊ ሆነው የተቀየሩበት
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    first_name = message.from_user.first_name or "ወዳጄ"
    
    user_memory[user_id] = []
    
    # 🔵 እዚህ ጋ ስሙን እና Senay Techን ሰማያዊ ማድረጊያ ሊንክ ተጠቅመናል
    blue_name = f"[{first_name}](tg://user?id={user_id})"
    blue_brand = "[Senay Tech](https://t.me/Senaytech)"
    
    welcome_text = (
        f"ሰላም {blue_name} 👋! እንኳን ደህና መጣህ።\n\n"
        f"እኔ በ {blue_brand} የሰለጠንኩ፣ ችግርን የምረዳ እና አብሬህ የምጓዝ የ AI ረዳት ነኝ። "
        f"ከአንተ ጋር በምቾት ለመጨዋወት እንድንችል እባክህ ጾታህን ምረጥልኝ፦"
    )
    
    markup = telebot.types.InlineKeyboardMarkup()
    btn_male = telebot.types.InlineKeyboardButton("ወንድ (ጀግናው) 🦁", callback_data="set_male")
    btn_female = telebot.types.InlineKeyboardButton("ሴት (ቆንጅት) ✨", callback_data="set_female")
    markup.add(btn_male, btn_female)
    
    bot.send_message(user_id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data in ["set_male", "set_female"])
def handle_gender_selection(call):
    user_id = call.message.chat.id
    first_name = call.message.chat.first_name or "ወዳጄ"
    blue_name = f"[{first_name}](tg://user?id={user_id})"
    
    if call.data == "set_male":
        user_gender[user_id] = "male"
        reply = f"እሺ ጀግናው {blue_name}! 🦁 ጾታህን አስተካክያለሁ። አሁን የፈለግከውን ጥያቄ ጠይቀኝ፣ ወንድሜ!"
    else:
        user_gender[user_id] = "female"
        reply = f"እሺ ቆንጅት {blue_name}! ✨ ጾታሽን አስተካክያለሁ። አሁን የሚሰማሽን ወይም ማወቅ የምትፈልጊውን ማንኛውንም ነገር ጠይቂኝ!"
        
    bot.answer_callback_query(call.id)
    bot.edit_message_text(reply, chat_id=user_id, message_id=call.message.message_id, parse_mode="Markdown")

def ask_gemini(user_id, user_text):
    gender = user_gender.get(user_id, "male")
    gender_instruction = (
        "ተጠቃሚው ወንድ ስለሆነ 'ጀግናው'፣ 'በርታ'፣ 'ወንድሜ' እያልክ አበረታታው" 
        if gender == "male" else 
        "ተጠቃሚዋ ሴት ስለሆነች 'ቆንጅት'፣ 'እህቴ' እያልክ በጥሩ የኢትዮጵያዊ ቀልድ ለዛ አረጋጋትና አበረታታት"
    )
    
    # 🔵 ለጌሚኒ ራሱ Senay Techን ሁልጊዜ በእንግሊዝኛ ብቻ እንዲጽፍ መመሪያ ጨምረንለታል
    system_instruction = (
        f"You are an AI assistant trained by 'Senay Tech'. {gender_instruction}. "
        "CRITICAL: Always write 'Senay Tech' in English exactly as 'Senay Tech', never translate it to Amharic. "
        "Be helpful, empathetic, friendly, and act like a real Ethiopian close friend. "
        "Use engaging Amharic with a touch of polite humor. Keep answers precise, scannable, and inspiring."
    )
    
    if user_id not in user_memory:
        user_memory[user_id] = []
        
    contents = []
    for past_user, past_ai in user_memory[user_id]:
        contents.append({"role": "user", "parts": [{"text": past_user}]})
        contents.append({"role": "model", "parts": [{"text": past_ai}]})
        
    contents.append({"role": "user", "parts": [{"text": user_text}]})
    
    payload = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    headers = {'Content-Type': 'application/json'}
    
    for index, key in enumerate(GEMINI_KEYS):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
            response = requests.post(url, headers=headers, json=payload, timeout=12)
            response_data = response.json()
            
            if 'error' in response_data:
                if response_data['error'].get('code') in [429, 503]:
                    time.sleep(2)
                    continue
                else:
                    return "✖️ በሲስተሙ ላይ ትንሽ ስህተት አጋጥሞኛል።"
            
            if 'candidates' in response_data:
                ai_reply = response_data['candidates'][0]['content']['parts'][0]['text']
                
                # 🔵 ጌሚኒ በጽሑፉ መሃል Senay Tech ካለ ሰማያዊ እንዲሆን በኮድ መተካት
                ai_reply = ai_reply.replace("Senay Tech", "[Senay Tech](https://t.me/Senaytech)")
                
                user_memory[user_id].append((user_text, ai_reply))
                if len(user_memory[user_id]) > 4:
                    user_memory[user_id].pop(0)
                    
                return ai_reply
                
        except Exception:
            time.sleep(2)
            continue
            
    return "⏳ ይቅርታ፣ በአሁኑ ሰዓት የጉግል ሲስተም በጣም ተጨናንቋል። እባክዎ ከጥቂት ሰከንዶች በኋላ መልሰው ይሞክሩ።"

@bot.message_handler(func=lambda message: True)
def handle_chat(message):
    user_id = message.chat.id
    current_time = time.time()
    
    last_time = user_last_time.get(user_id, 0)
    if current_time - last_time < 7:
        remaining = int(7 - (current_time - last_time))
        bot.reply_to(message, f"🚨 እባክህ አትቸኩል ጀግናው! አእምሮዬ እንዳይጨናነቅ {remaining} ሰከንድ ጠብቀኝ።")
        return
        
    user_last_time[user_id] = current_time
    status_message = None
    
    try:
        user_text = message.text
        gender = user_gender.get(user_id, "male")
        
        # 🔵 በማሰብ ላይ... መልእክት ውስጥ Senay Tech ሰማያዊ የተደረገበት
        blue_brand = "[Senay Tech](https://t.me/Senaytech)"
        thinking_text = "🤔 ለማሰብ ጥቂት ሰከንድ ስጠኝ ጀግናው...\n\n" if gender == "male" else "🤔 ለማሰብ ጥቂት ሰከንድ ስጪኝ ቆንጅት...\n\n"
        thinking_text += f"የባለሙያ የቴክኖሎጂ መረጃዎችን ለማግኘት የ {blue_brand} ቻናላችንን ይቀላቀሉ! 🚀"
        
        status_message = bot.reply_to(message, thinking_text, parse_mode="Markdown")
        
        ai_reply = ask_gemini(user_id, user_text)
        
        # 🔵 እዚህ ጋ parse_mode="Markdown" መኖሩን ማረጋገጥ አለብን ሊንኩ ሰማያዊ እንዲሆን
        bot.edit_message_text(ai_reply, chat_id=user_id, message_id=status_message.message_id, parse_mode="Markdown")
            
    except Exception as e:
        if status_message:
            bot.edit_message_text("❌ እባክህ በድጋሚ ሞክር፣ ትንሽ የኔትወርክ መቆራረጥ አጋጥሞኛል።", chat_id=user_id, message_id=status_message.message_id)
        else:
            bot.reply_to(message, "❌ እባክህ በድጋሚ ሞክር፣ ትንሽ የኔትወርክ መቆራረጥ አጋጥሞኛል።")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
