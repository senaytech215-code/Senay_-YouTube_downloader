import telebot
import os
import google.generativeai as genai

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
genai.configure(api_key=os.environ.get('GEMINI_KEY'))

# ሞዴልን በስም መጥራት ትተን የ'generative_model' ተግባርን እንጠቀም
model = genai.GenerativeModel('gemini-pro') 

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "አሁን ትንሽ ተጨናንቄያለሁ፣ ትንሽ ቆይተህ ሞክር።")

bot.infinity_polling()
