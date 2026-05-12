import telebot
import os
import google.generativeai as genai

BOT_TOKEN = os.environ.get('BOT_TOKEN')
AI_KEY = os.environ.get('GEMINI_KEY')

# AIውን በአዲሱ መንገድ ያዘጋጃል
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # ይሄኛው ይበልጥ ፈጣንና አዲስ ነው

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        # ስህተቱ ምን እንደሆነ ለየብቻ ይነግረናል
        error_msg = f"ኧረ ባክህ! ስህተት ተፈጠረ። \nዝርዝር፦ {str(e)}"
        bot.reply_to(message, error_msg)

if __name__ == '__main__':
    bot.infinity_polling()
