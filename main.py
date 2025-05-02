from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# توکن رباتت رو اینجا بذار
TOKEN = "7976346746:AAGF9wqw-B122eiUOAi1qOwgBABbD5MgaWA"  # توکنی که از BotFather گرفتی
# آیدی کانال رو اینجا بذار (مثلاً @MyChannel)
CHANNEL_ID = "@JaSignal"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # بررسی عضویت کاربر در کانال
    member = await context.bot.get_chat_member(CHANNEL_ID, user.id)
    if member.status in ["member", "administrator", "creator"]:
        await update.message.reply_text("شما عضو کانال هستید! حالا می‌تونید از امکانات ربات استفاده کنید.")
    else:
        # دکمه برای عضویت در کانال
        keyboard = [
            [InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{CHANNEL_ID[1:]}")],
            [InlineKeyboardButton("بررسی عضویت", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "لطفاً اول در کانال ما عضو بشید:", reply_markup=reply_markup
        )

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    # بررسی دوباره عضویت
    member = await context.bot.get_chat_member(CHANNEL_ID, user.id)
    if member.status in ["member", "administrator", "creator"]:
        await query.message.reply_text("تبریک! حالا شما عضو کانال هستید!")
    else:
        await query.message.reply_text("شما هنوز عضو کانال نشدید. لطفاً در کانال عضو بشید.")

def main():
    # ساخت اپلیکیشن ربات
    app = Application.builder().token(TOKEN).build()
    # اضافه کردن دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_membership, pattern="check_membership"))
    # اجرای ربات
    app.run_polling()

if __name__ == "__main__":
    main()