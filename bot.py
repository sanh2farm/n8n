import os
import logging
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import pytesseract
from PIL import Image
import io

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database tạm
products = {
    "1": {"name": "Áo thun", "price": 150000, "stock": 10},
    "2": {"name": "Quần jean", "price": 350000, "stock": 5},
    "3": {"name": "Giày thể thao", "price": 500000, "stock": 8},
}

user_state = {}   # quản lý trạng thái OCR


# ============================
#  MENU CHÍNH
# ============================

def main_menu():
    keyboard = [
        [KeyboardButton("🛒 Mua hàng")],
        [KeyboardButton("💼 Bán hàng")],
        [KeyboardButton("📸 Chuyển ảnh sang chữ")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ============================
#  START
# ============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Chào bạn!\nChọn chức năng bên dưới:",
        reply_markup=main_menu()
    )


# ============================
#  MUA HÀNG
# ============================

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🛍️ *DANH SÁCH SẢN PHẨM*\n\n"
    keyboard = []

    for pid, p in products.items():
        text += f"*{pid}. {p['name']}*\n💰 {p['price']:,}đ — 📦 {p['stock']}\n\n"
        keyboard.append([
            InlineKeyboardButton(f"Mua {p['name']}", callback_data=f"buy_{pid}")
        ])

    await update.message.reply_text(
        text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pid = query.data.split("_")[1]

    if products[pid]["stock"] > 0:
        products[pid]["stock"] -= 1
        await query.edit_message_text(
            f"✅ Đã mua *{products[pid]['name']}* thành công!",
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text("❌ Hết hàng!")

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Bạn muốn làm gì tiếp?",
        reply_markup=main_menu()
    )


# ============================
#  BÁN HÀNG
# ============================

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💼 Gửi theo mẫu để thêm sản phẩm:\n\n"
        "`/add Tên | Giá | Số lượng`",
        parse_mode="Markdown"
    )


async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        _, data = update.message.text.split(" ", 1)
        name, price, stock = [x.strip() for x in data.split("|")]

        new_id = str(len(products) + 1)

        products[new_id] = {
            "name": name,
            "price": int(price),
            "stock": int(stock)
        }

        await update.message.reply_text("✅ Đã thêm sản phẩm!")

    except:
        await update.message.reply_text("❌ Sai định dạng!")


# ============================
#  OCR – CHUYỂN ẢNH SANG CHỮ
# ============================

async def request_ocr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_state[user_id] = "waiting_ocr"

    await update.message.reply_text(
        "📸 Gửi ảnh chứa văn bản để chuyển sang chữ."
    )


async def handle_ocr_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_state.get(user_id) != "waiting_ocr":
        return

    await update.message.reply_text("⏳ Đang xử lý ảnh...")

    photo_file = await update.message.photo[-1].get_file()
    image_bytes = await photo_file.download_as_bytearray()

    img = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(img, lang="vie+eng")

    if text.strip():
        await update.message.reply_text(f"📄 *Kết quả OCR:*\n\n{text}", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Không nhận được chữ nào!")

    user_state[user_id] = None
    await update.message.reply_text("Hoàn tất!", reply_markup=main_menu())


# ============================
#  ROUTER – xử lý text
# ============================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text

    if msg == "🛒 Mua hàng":
        await show_products(update, context)

    elif msg == "💼 Bán hàng":
        await sell(update, context)

    elif msg == "📸 Chuyển ảnh sang chữ":
        await request_ocr(update, context)


# ============================
#  MAIN
# ============================

def main():
    TOKEN = os.getenv("7596346317:AAGC9fhDW-iCDeFZW46pfMF3ydwOXO9KWqQ")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_product))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_ocr_image))
    app.add_handler(CallbackQueryHandler(handle_buy, pattern="^buy_"))

    print("Bot is running…")
    app.run_polling()


if __name__ == "__main__":
    main()
