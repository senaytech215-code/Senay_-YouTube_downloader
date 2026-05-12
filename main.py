import telebot
import os

# ቶክኑን ከ Render ይወስዳል
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ሰላም ሰናይ! አሁን ቦቱ በሰላም ሰርቷል። የ AI አእምሮውን ለመጫን ዝግጁ ነኝ!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    # የላክህለትን መልእክት መልሶ ይልክልሃል
    bot.reply_to(message, f"የላክኸው መልእክት፦ {message.text}")

if __name__ == '__main__':
    print("Test Bot is Live! 🚀")
    bot.infinity_polling()
