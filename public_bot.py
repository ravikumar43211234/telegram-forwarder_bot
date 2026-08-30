import os
import re
import logging
import requests
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. DUMMY WEB SERVER FOR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "LootersGang Affiliate Bot is Alive & Running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

keep_alive()

# --- 2. CONFIGURATION ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = "8750109986:AAGR1qkaQI1Tbw58x24VlAGyV11fhNAXXzQ"

# Aapka EarnKaro JWT Auth Token
EARNKARO_JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2YTgxYTYyZGRlMTUxZTUyZDMyYjllNWEiLCJlYXJua2FybyI6IjU1NDQ0NDUiLCJpYXQiOjE3ODgwNDE4MTl9.3HqB-FNw5fTYENqQA6NzDUDt67QYoRkVGTz784-mDEk"

# --- 3. CONVERT LINK USING JWT AUTHORIZATION ---
def convert_to_earnkaro(original_url):
    try:
        # EarnKaro Link Conversion API
        api_url = "https://earnkaro.com/api/v1/make-link"
        
        headers = {
            "Authorization": f"Bearer {EARNKARO_JWT_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        payload = {
            "link": original_url
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Response handling for converted profit link
            if "profit_link" in data:
                return data["profit_link"]
            elif "data" in data and "profit_link" in data["data"]:
                return data["data"]["profit_link"]
            elif "url" in data:
                return data["url"]
        
        # Fallback redirect URL generation
        encoded_url = requests.utils.quote(original_url, safe='')
        return f"https://earnkaro.com/share?url={encoded_url}"

    except Exception as e:
        print(f"Error converting link: {e}")
        encoded_url = requests.utils.quote(original_url, safe='')
        return f"https://earnkaro.com/share?url={encoded_url}"

# --- 4. BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **Welcome to LootersGang Affiliate Converter Bot!**\n\n"
        "Mujhe kisi bhi product ka link (Amazon, Flipkart, Myntra, Ajio, etc.) bhejo, "
        "main Instant EarnKaro Affiliate Link mein convert karke de dunga."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Extract URLs from message
    urls = re.findall(r'https?://[^\s]+', user_text)
    
    if not urls:
        await update.message.reply_text("❌ Kripya koi valid deal link/URL bhejein.")
        return
        
    status_msg = await update.message.reply_text("⏳ *Converting your link...*", parse_mode="Markdown")
    
    converted_text = user_text
    has_converted = False
    
    for url in urls:
        affiliate_url = convert_to_earnkaro(url)
        if affiliate_url:
            converted_text = converted_text.replace(url, affiliate_url)
            has_converted = True
            
    if has_converted:
        await status_msg.edit_text(f"✅ **Converted Deal Link:**\n\n{converted_text}")
    else:
        await status_msg.edit_text("❌ Link convert nahi ho saka.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running with JWT Authentication...")
    application.run_polling()

if __name__ == '__main__':
    main()
