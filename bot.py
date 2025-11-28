from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "YOUR_BOT_TOKEN"

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
        await update.message.reply_text("Gửi ảnh cho tôi nhé!")
    else:
        await update.message.reply_text("Hãy chọn nút bên dưới!")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    print("BOT STARTED")
    app.run_polling()
