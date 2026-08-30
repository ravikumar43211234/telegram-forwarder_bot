import os
import json
import requests
from threading import Thread
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ==================== DUMMY WEB SERVER FOR RENDER ====================
app_web = Flask('')

@app.route('/')
def home():
    return "🤖 LootersGang Public Converter Bot is Alive & Running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

keep_alive()
# =====================================================================

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8750109986:AAGR1qkaQI1Tbw58x24VlAGyV11fhNAXXzQ"
AFFILIATERS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2YTgxYTYyZGRlMTUxZTUyZDMyYjllNWEiLCJlYXJua2FybyI6IjU1NDQ0NDUiLCJpYXQiOjE3ODgwNDE4MTl9.3HqB-FNw5fTYENqQA6NzDUDt67QYoRkVGTz784-mDEk"

BASE_URL = "https://ekaro-api.affiliaters.in/api/converter/public"
CHANNEL_URL = "https://t.me/LootersGang_Deals"
# =======================================================

def convert_deal_via_affiliaters(user_text):
    headers = {
        'Authorization': f'Bearer {AFFILIATERS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = json.dumps({
        "deal": user_text,
        "convert_option": "convert_only"
    })
    
    try:
        response = requests.post(BASE_URL, headers=headers, data=payload, timeout=15)
        res_data = response.json()
        
        if response.status_code == 200 and "data" in res_data:
            return res_data["data"]
        elif "converted_text" in res_data:
            return res_data["converted_text"]
        elif "message" in res_data:
            return res_data["message"]
        else:
            return None
    except Exception as e:
        print(f"API Call Error: {e}")
        return None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    
    keyboard = [
        [InlineKeyboardButton("📢 Join Main Channel", url=CHANNEL_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"👋 **Hello {user_name}!**\n\n"
        "Welcome to **LootersGang Link Converter Bot** ⚡\n\n"
        "📌 **Kaise use karein?**\n"
        "Amazon, Flipkart, Myntra ya kisi bhi store ka deal message ya link yahan bhejein. "
        "Hum usko instantly affiliate link mein convert kar denge.\n\n"
        "👇 Daily heavy loots ke liye humara channel join karein:"
    )

    await update.message.reply_text(
        text=welcome_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "❓ **Help / Kaise Convert Karein?**\n\n"
        "1. Kisi bhi deal message ya shopping link ko copy karein.\n"
        "2. Is bot mein send / paste kar dein.\n"
        "3. Bot aapko instant converted affiliate link reply kar dega.\n\n"
        "📢 Main Channel: @LootersGang_Deals"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔥 Top Loot Deals ke liye humara main channel join karein:", reply_markup=reply_markup)

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    incoming_text = update.message.text
    status_msg = await update.message.reply_text("⏳ Converting link, please wait...")

    converted_result = convert_deal_via_affiliaters(incoming_text)

    if converted_result:
        final_response = f"{converted_result}\n\n🔥 **Join for Daily Loot Deals:**\n👉 {CHANNEL_URL}"
        await status_msg.edit_text(final_response, disable_web_page_preview=False)
    else:
        await status_msg.edit_text("❌ Link convert nahi ho paaya. Kripya valid shopping link bhejain.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("channel", channel_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_user_message))
    
    print("🤖 LootersGang Public Converter Bot is Live & Running...")
    app.run_polling()
