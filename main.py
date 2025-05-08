import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio

# تنظیم توکن و آیدی کانال
TOKEN = "7665575293:AAGyuK6D5kS-cnL-76ojQRfP1jCmKLjPHR0"  # توکن جدید
CHANNEL_ID = "@RoyalGuardX"  # کانال (اگر عوض شده، تغییر بده)

# ایجاد اپلیکیشن Flask
app = Flask(__name__)

# ایجاد اپلیکیشن تلگرام
bot_app = Application.builder().token(TOKEN).build()

# تابع برای دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user.id)
        if member.status in ["member", "administrator", "creator"]:
            await update.message.reply_text("شما عضو کانال هستید! حالا می‌تونید از امکانات ربات استفاده کنید.")
        else:
            keyboard = [
                [InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{CHANNEL_ID[1:]}")],
                [InlineKeyboardButton("بررسی عضویت", callback_data="check_membership")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "لطفاً اول در کانال ما عضو بشید:", reply_markup=reply_markup
            )
    except Exception as e:
        await update.message.reply_text(f"خطایی رخ داد: {str(e)}")

# تابع برای بررسی عضویت
async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user.id)
        if member.status in ["member", "administrator", "creator"]:
            await query.message.reply_text("تبریک! حالا شما عضو کانال هستید!")
        else:
            await query.message.reply_text("شما هنوز عضو کانال نشدید. لطفاً در کانال عضو بشید.")
    except Exception as e:
        await query.message.reply_text(f"خطایی رخ داد: {str(e)}")

# اضافه کردن هندلرها
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(check_membership, pattern="check_membership"))

# مسیر Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot_app.bot)
        asyncio.run(bot_app.process_update(update))  # پردازش آپدیت با asyncio
        return "OK", 200
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return "Error", 500

# تنظیم Webhook موقع شروع سرور
@app.route("/")
def set_webhook():
    try:
        webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
        asyncio.run(bot_app.bot.set_webhook(webhook_url))  # استفاده از asyncio.run
        return "Webhook set successfully", 200
    except Exception as e:
        return f"Failed to set webhook: {str(e)}", 500

# تابع برای تنظیم اولیه Webhook
async def init_bot():
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    await bot_app.bot.set_webhook(webhook_url)
    print(f"Webhook set to {webhook_url}")

# اجرای سرور
if __name__ == "__main__":
    port = int(os.getenv("PORT", 80))  # پورت 80 برای Render
    asyncio.run(init_bot())  # تنظیم Webhook اولیه
    app.run(host="0.0.0.0", port=port)
