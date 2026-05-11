import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import yt_dlp

# Render ላይ BOT_TOKEN ብለህ ያስገባኸውን ያነባል
TOKEN = os.environ.get('BOT_TOKEN')
# እዚህ ጋር የቻናልህን ሊንክ አስገባ
CHANNEL_LINK = "https://t.me/Senay_Tech" 

async def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" in url or "youtu.be" in url:
        await update.message.reply_text("ቪዲዮውን በማውረድ ላይ ነኝ... እባክዎ የቴሌግራም ቻናላችንን ይቀላቀሉ፡ " + CHANNEL_LINK)
        try:
            await download_video(url)
            with open('video.mp4', 'rb') as video:
                await update.message.reply_video(video=video, caption=f"ባለቤት፡ @Senay_Tech \nቻናላችንን ይቀላቀሉ፡ {CHANNEL_LINK}")
            os.remove('video.mp4')
        except Exception as e:
            await update.message.reply_text(f"ስህተት አጋጥሟል፦ {e}")
    else:
        await update.message.reply_text("እባክዎ ትክክለኛ የዩቲዩብ ሊንክ ይላኩ።")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("ቦቱ ስራ ጀምሯል...")
    app.run_polling()
