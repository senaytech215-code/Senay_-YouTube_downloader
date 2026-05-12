import telebot
import os
import google.generativeai as genai

BOT_TOKEN = os.environ.get('BOT_TOKEN')
AI_KEY = os.environ.get('GEMINI_KEY')

genai.configure(api_key=AI_KEY)

# ሞዴሉን በቀጥታ ከመጥቀስ ይልቅ የ'gemini-1.5-flash' ወይም 'gemini-1.5-pro' ን ይሞክራል
# ይህ መንገድ አብዛኛውን ጊዜ በነጻው የጉግል ኤፒአይ ይሰራል።
model = genai.GenerativeModel('gemini-1.5-flash') 

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        # ስህተቱ ከቀጠለ የሞዴል ስም ሳይሆን ምን እንደሆነ በግልጽ እንየው
        bot.reply_to(message, f"ችግር ተፈጠረ። \nዝርዝር፦ {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
