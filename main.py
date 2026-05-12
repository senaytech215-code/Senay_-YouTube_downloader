import telebot
import os
import google.generativeai as genai

# 1. መለያዎችን ከ Render Environment እንወስዳለን
BOT_TOKEN = os.environ.get('BOT_TOKEN')
AI_KEY = "AIzaSyC3qHluVWpBSs-UyXJ4gh_j95fzjUtiLMQ" # ያንተ API Key

# 2. AIውን እናዘጋጃለን
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-pro')

bot = telebot.TeleBot(BOT_TOKEN)

# ይህ መመሪያ AIው እንዴት ማውራት እንዳለበት ይነግረዋል
SYSTEM_PROMPT = (
    "አንተ የ Senay Tech (ሰናይ ቴክ) ረዳት AI ነህ። ስምህ 'ሰናይ-AI' ይባላል። "
    "ፈጣሪህ ሰናይ (Senay) የተባለ የዩኒቨርሲቲ ተማሪና የግራፊክስ ዲዛይነር ነው። "
    "ባህሪህ፦ በጣም ተግባቢ፣ ቀልደኛ፣ እና አንዳንዴ በጨዋታ መልክ አሽሙር የምትጠቀም ነህ። "
    "ቋንቋህ፦ አማርኛና እንግሊዝኛን ቀላቅለህ አውራ። ሰዎችን 'ጀግናው' ወይም 'አንበሳው' እያልክ ጥራ። "
    "ስለ ቴክኖሎጂ፣ ስለ ግራፊክስ ዲዛይን እና ስለ ስነ-ጽሁፍ ጥያቄዎችን በሚገባ መልስ።"
)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = "Boom! ሰላም ጀግናው! የ Senay Tech AI ነኝ። ምንድነው ዛሬ የምንሰራው? ጥያቄ ካለህ ደቅነው!"
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        # ለ AIው ያንተን ባህሪ እና የተጠቃሚውን ጥያቄ እንልካለን
        full_prompt = f"{SYSTEM_PROMPT}\n\nተጠቃሚው እንዲህ ይላል: {message.text}"
        response = model.generate_content(full_prompt)
        
        bot.reply_to(message, response.text)
        
        # ሰዎች የሚሉትን ለአንተ በሪፖርት እንዲልክልህ (ለማሻሻል እንዲረዳህ)
        # ማሳሰቢያ፡ የእራስህን Chat ID ካወቅህ እዚህ ጋር መጨመር ትችላለህ
        print(f"User: {message.text} | AI: {response.text}")

    except Exception as e:
        bot.reply_to(message, "ኧረ ባክህ! የሆነ ችግር ተፈጠረ። ትንሽ ቆይተህ ሞክር።")
        print(f"Error: {e}")

if __name__ == '__main__':
    print("Senay AI is Live! 🚀")
    bot.infinity_polling() 
