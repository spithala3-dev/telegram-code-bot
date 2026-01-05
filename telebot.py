import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ===== ENV VARIABLES (SAFE FOR GITHUB) =====
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ===== STORAGE =====
codes = {}          # {number: code}
valid_codes = set()
mode = None         # None | "add_codes" | "mark_valid"

# ===== SECURITY =====
def is_admin(update: Update):
    return update.effective_user.id == ADMIN_ID

# ===== UI KEYBOARD =====
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Code List", callback_data="add")],
        [InlineKeyboardButton("✅ Mark Valid Codes", callback_data="mark")],
        [InlineKeyboardButton("📋 Show Valid Codes", callback_data="show")],
        [InlineKeyboardButton("🔄 Reset List", callback_data="reset")]
    ])

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    await update.message.reply_text(
        "👋 **Admin Panel**\n\n"
        "Choose an action below 👇",
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )

# ===== BUTTON HANDLER =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global mode
    if not is_admin(update):
        return

    query = update.callback_query
    await query.answer()

    if query.data == "add":
        mode = "add_codes"
        await query.message.reply_text(
            "➕ **Paste code list** like:\n\n"
            "1. CODE123\n"
            "2. CODE456\n"
            "3. CODE789",
            parse_mode="Markdown"
        )

    elif query.data == "mark":
        if not codes:
            await query.message.reply_text("❌ No codes added yet.")
            return
        mode = "mark_valid"
        await query.message.reply_text(
            "✅ Send **valid code numbers** like:\n\n`1,3,5`",
            parse_mode="Markdown"
        )

    elif query.data == "show":
        if not valid_codes:
            await query.message.reply_text("❌ No valid codes marked yet.")
            return

        msg = "📋 **VALID CODES (Copy Below)**\n\n"
        for i in sorted(valid_codes):
            msg += f"{codes[i]}\n"

        await query.message.reply_text(msg, parse_mode="Markdown")

    elif query.data == "reset":
        codes.clear()
        valid_codes.clear()
        mode = None
        await query.message.reply_text(
            "🔄 **All data reset**",
            reply_markup=main_keyboard(),
            parse_mode="Markdown"
        )

# ===== TEXT HANDLER =====
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global mode
    if not is_admin(update):
        return

    text = update.message.text.strip()

    # ADD CODES
    if mode == "add_codes":
        codes.clear()
        valid_codes.clear()

        for line in text.split("\n"):
            if "." in line:
                try:
                    n, c = line.split(".", 1)
                    codes[int(n.strip())] = c.strip()
                except:
                    pass

        mode = None
        await update.message.reply_text(
            "✅ **Codes saved successfully**",
            reply_markup=main_keyboard(),
            parse_mode="Markdown"
        )

    # MARK VALID
    elif mode == "mark_valid":
        for n in text.split(","):
            try:
                valid_codes.add(int(n.strip()))
            except:
                pass

        mode = None
        await update.message.reply_text(
            "✅ **Valid codes updated**",
            reply_markup=main_keyboard(),
            parse_mode="Markdown"
        )

# ===== APP START =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
