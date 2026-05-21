import os
import telebot
import time
from flask import Flask, request
from google import genai
from google.genai import types

BOT_TOKEN = os.environ.get('BOT_TOKEN')
# 3ቱን ቁልፎች በዝርዝር መያዝ
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
all_users = set()

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'ok', 200
    return 'Senay Tech Official GenAI Server is Running!', 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    first_name = message.from_user.first_name or "ወዳጄ"
    
    all_users.add(user_id)
    user_memory[user_id] = []
    
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

@bot.message_handler(commands=['admin'])
def check_users(message):
    user_id = message.chat.id
    # ⚠️ ማሳሰቢያ: የራስህን መታወቂያ ቁጥር እዚህ ጋር መተካት ትችላለህ
    if user_id == 703353544: # ምሳሌ ID
        total = len(all_users)
        bot.reply_to(message, f"📊 **የሰናይ ቴክ ቦት መረጃ**\n\n• ጠቅላላ የቦቱ ተመዝጋቢዎች ብዛት፦ `{total}` ሰዎች", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ ይቅርታ፣ ይህ ትዕዛዝ ለቦቱ ባለቤት (Admin) ብቻ የተፈቀደ ነው!")

def ask_gemini(user_id, user_text):
    gender = user_gender.get(user_id, "male")
    gender_instruction = (
        "ተጠቃሚው ወንድ ስለሆነ 'ጀግናው'፣ 'በርታ'፣ 'ወንድሜ' እያልክ አበረታታው" 
        if gender == "male" else 
        "ተጠቃሚዋ ሴት ስለሆነች 'ቆንጅት'፣ 'እህቴ' እያልክ በጥሩ የኢትዮጵያዊ ቀልድ ለዛ አበረታታት"
    )
    
    system_instruction = (
        f"You are an AI assistant trained by 'Senay Tech'. {gender_instruction}. "
        "CRITICAL: Always write 'Senay Tech' in English exactly as 'Senay Tech', never translate it to Amharic. "
        "Be helpful, empathetic, friendly, and act like a real Ethiopian close friend. "
        "Use engaging Amharic with a touch of polite humor. Keep answers precise, scannable, and inspiring."
    )
    
    if user_id not in user_memory:
        user_memory[user_id] = []
        
    # በኦፊሴላዊው መንገድ የውይይት ታሪክን ማዘጋጀት
    history_contents = []
    for past_user, past_ai in user_memory[user_id]:
        history_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=past_user)]))
        history_contents.append(types.Content(role="model", parts=[types.Part.from_text(text=past_ai)]))
    
    # አዲሱን ጥያቄ መጨመር
    history_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_text)]))
    
    # እያንዳንዱን ቁልፍ በየተራ መሞከር
    for index, key in enumerate(GEMINI_KEYS):
        try:
            # 🔵 የጉግል ኦፊሴላዊ ደንበኛ (Client) ማስነሻ
            client = genai.Client(api_key=key)
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=history_contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            
            if response.text:
                ai_reply = response.text
                ai_reply = ai_reply.replace("Senay Tech", "[Senay Tech](https://t.me/Senaytech)")
                
                user_memory[user_id].append((user_text, ai_reply))
                if len(user_memory[user_id]) > 4:
                    user_memory[user_id].pop(0)
                    
                return ai_reply
                
        except Exception as e:
            print(f"Key {index+1} Exception: {str(e)}")
            time.sleep(2)
            continue
            
    return "⏳ ይቅርታ፣ በአሁኑ ሰዓት የጉግል ሲስተም በጣም ተጨናንቋል። እባክዎ ከ1 ደቂቃ በኋላ መልሰው ይሞክሩ።"

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
        
        blue_brand = "[Senay Tech](https://t.me/Senaytech)"
        thinking_text = "🤔 ለማሰብ ጥቂት ሰከንድ ስጠኝ ጀግናው...\n\n" if gender == "male" else "🤔 ለማሰብ ጥቂት ሰከንድ ስጪኝ ቆንጅት...\n\n"
        thinking_text += f" ጠቃሚ የቴክኖሎጂ መረጃዎችን ለማግኘት የ {blue_brand} ቻናላችንን ይቀላቀሉ! 🚀"
        
        status_message = bot.reply_to(message, thinking_text, parse_mode="Markdown")
        
        ai_reply = ask_gemini(user_id, user_text)
        bot.edit_message_text(ai_reply, chat_id=user_id, message_id=status_message.message_id, parse_mode="Markdown")
            
    except Exception:
        if status_message:
            bot.edit_message_text("❌ እባክህ በድጋሚ ሞክር፣ ትንሽ የኔትወርክ መቆራረጥ አጋጥሞኛል።", chat_id=user_id, message_id=status_message.message_id)
        else:
            bot.reply_to(message, "❌ እባክህ በድጋሚ ሞክር፣ ትንሽ የኔትወርክ መቆራረጥ አጋጥሞኛል።")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
