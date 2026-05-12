import telebot
import os
import google.generativeai as genai

# መለያዎችን ከ Render Environment (ደህንነቱ በተጠበቀ መንገድ) ይወስዳል
BOT_TOKEN = os.environ.get('BOT_TOKEN')
AI_KEY = os.environ.get('GEMINI_KEY')

# AIውን ያዘጋጃል
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-pro')

bot = telebot.TeleBot(BOT_TOKEN)

SYSTEM_PROMPT = (
    "አንተ የ Senay Tech (ሰናይ ቴክ) ረዳት AI ነህ። ስምህ 'ሰናይ-AI' ይባላል። "
    "ፈጣሪህ ሰናይ የተባለ የዩኒቨርሲቲ ተማሪና የግራፊክስ ዲዛይነር ነው። "
    "ባህሪህ፦ ተግባቢ፣ ቀልደኛና አንዳንዴ አሽሙር የምትጠቀም ነህ። "
    "በአማርኛና በእንግሊዝኛ ድብልቅ አውራ።"
)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Boom! ሰላም ጀግናው! ሰናይ-AI ነኝ። ምንድነው ዛሬ የምንሰራው?")

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {message.text}"
        response = model.generate_content(full_prompt)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "ኧረ ባክህ! የሆነ ችግር ተፈጠረ። ትንሽ ቆይተህ ሞክር።")

if __name__ == '__main__':
    print("Senay AI is Live and Secure! 🚀")
    bot.infinity_polling() 

