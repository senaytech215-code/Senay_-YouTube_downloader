import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import yt_dlp

# Render Environment ላይ BOT_TOKEN ብለህ የሞላኸውን ያነባል
TOKEN = os.environ.get('BOT_TOKEN')

# --- ያንተ መረጃዎች ---
MY_CHANNEL_URL = "https://t.me/Senaytech" 
MY_CHANNEL_NAME = "@Senaytech"

async def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'youtube_video.mp4',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'addheader': [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        ],
        'referer': 'https://www.google.com/',
    }
    
    if os.path.exists('youtube_video.mp4'):
        os.remove('youtube_video.mp4')
        
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_url = update.message.text
    
    # የዩቲዩብ ሊንክ መሆኑን ቼክ ለማድረግ (YouTube ወይም youtu.be ካለበት)
    if "youtube.com" in user_url or "youtu.be" in user_url:
        await update.message.reply_text(f"ቪዲዮውን በማውረድ ላይ ነኝ... ⏳\nእስከዚያው ቻናላችንን ይቀላቀሉ፦ {MY_CHANNEL_URL}")
        
        try:
            await download_video(user_url)
            
            if os.path.exists('youtube_video.mp4'):
                with open('youtube_video.mp4', 'rb') as video_file:
                    await update.message.reply_video(
                        video=video_file, 
                        caption=f"🎬 ቪዲዮው ዝግጁ ነው!\n\nባለቤት፦ {MY_CHANNEL_NAME}\nተጨማሪ ቪዲዮዎችን ለማግኘት ቻናላችንን ይቀላቀሉ፦ {MY_CHANNEL_URL}"
                    )
                os.remove('youtube_video.mp4')
            else:
                await update.message.reply_text("ይቅርታ፣ ቪዲዮውን ማውረድ አልቻልኩም።")
                
        except Exception as e:
            await update.message.reply_text(f"ስህተት፦ ዩቲዩብ ለጊዜው አግዶኛል። እባክዎ ትንሽ ቆይተው ይሞክሩ።")
    else:
        await update.message.reply_text("እባክዎ ትክክለኛ የዩቲዩብ ሊንክ ብቻ ይላኩ።")

if __name__ == '__main__':
    if not TOKEN:
        print("Error: BOT_TOKEN is missing!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        print("ቦቱ ስራ ጀምሯል...")
        app.run_polling()
