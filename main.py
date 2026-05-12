import telebot
import os
import google.generativeai as genai

# መለያዎችን ከ Render Environment (ደህንነቱ በተጠበቀ መንገድ) ይወስዳል
BOT_TOKEN = os.environ.get('BOT_TOKEN')
AI_KEY = os.environ.get('GEMINI_KEY')

# AIውን ያዘጋጃል
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-pro') # አሁን ወደ አስተማማኙ ሞዴል ተቀይሯል

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        # የላክኸውን መልእክት ወደ AI ይልካል
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        # ስህተት ቢፈጠር ለይቶ ይነግረናል
        bot.reply_to(message, f"ኧረ ባክህ! ስህተት ተፈጠረ። \nዝርዝር፦ {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling() 
