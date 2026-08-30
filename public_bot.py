import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. DUMMY WEB SERVER FOR RENDER PORT BINDING ---
app = Flask('')

@app.route('/')
def home():
    return "LootersGang Converter Bot is Alive & Running!"

def run():
    # Render automatically PORT environment variable assign karta hai
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# Flask Web Server ko background mein start karein
keep_alive()

# --- 2. BOT LOGIC & CONFIGURATION ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Yahan apna Bot Token check kar lein
BOT_TOKEN = "8750109986:AAEo_P9314F7Ns6q1X86snqeQebU6PyRDWg"  # Aapka bot token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Mujhe koi bhi product link bhejo, main use affiliate link me convert kar dunga.")

async def convert_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # Aapka link conversion logic
    await update.message.reply_text(f"Converted Link: {user_text}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert_link))
    
    print("LootersGang Public Converter Bot is Live & Running...")
    application.run_polling()

if __name__ == '__main__':
    main()
