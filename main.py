import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import yt_dlp

# --- እዚህ ጋር ከ BotFather ያገኘኸውን Token አስገባ ---
TOKEN = '8252976058:AAEBdEX6blyV1tlr5MbrlMNuA4ciNNhv9GM'

async def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" in url or "youtu.be" in url:
        await update.message.reply_text("ቪዲዮውን በማውረድ ላይ ነኝ፣ እባክዎ ትንሽ ይጠብቁ... ⏳")
        try:
            await download_video(url)
            await update.message.reply_video(video=open('video.mp4', 'rb'))
            os.remove('video.mp4') # ፋይሉን ከስልካችን ላይ እናጠፋለን
        except Exception as e:
            await update.message.reply_text(f"ይቅርታ ስህተት አጋጥሟል፦ {e}")
    else:
        await update.message.reply_text("እባክዎ ትክክለኛ የዩቲዩብ ሊንክ ይላኩ።")

if name == 'main':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("ቦቱ ስራ ጀምሯል...")
    app.run_polling() 
