import os
import threading
import asyncio

from fastapi import FastAPI
import uvicorn

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔥 TOKEN BOT — nhớ thay bằng token mới!!!
TOKEN = "7596346317:AAGC9fhDW-iCDeFZW46pfMF3ydwOXO9KWqQ"

# --- MENU TELEGRAM ---
main_menu = ReplyKeyboardMarkup(
    [
        ["Mua Hàng", "Bán Hàng"],
        ["Chuyển ảnh → văn bản"]
    ],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Chào bạn! Đây là menu:", reply_markup=main_menu)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Mua Hàng":
        await update.message.reply_text("Bạn chọn Mua Hàng.")
    elif text == "Bán Hàng":
        await update.message.reply_text("Bạn chọn Bán Hàng.")
    elif text == "Chuyển ảnh → văn bản":
        await update.message.reply_text("Gửi ảnh cho tôi để chuyển sang văn bản!")
    else:
        await update.message.reply_text("Hãy chọn nút bên dưới!")

# --- TELEGRAM BOT ---
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- FASTAPI PING SERVER ---
app_api = FastAPI()

@app_api.get("/")
async def root():
    return {"status": "Bot is alive"}

def run_bot():
    application.run_polling()

# Chạy Telegram bot song song
threading.Thread(target=run_bot).start()

# --- CHẠY FASTAPI TRÊN PORT CỦA RENDER ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render sẽ gán PORT vào đây
    uvicorn.run(app_api, host="0.0.0.0", port=port)
