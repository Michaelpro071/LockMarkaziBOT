import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
import asyncio

# تنظیم لاگ‌گیری
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# تنظیم توکن و آیدی کانال
TOKEN = "7665575293:AAGyuK6D5kS-cnL-76ojQRfP1jCmKLjPHR0"
CHANNEL_ID = "@RoyalGuardX"  # کانال رو چک کن

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
        logger.error(f"Error in start: {str(e)}")
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
        logger.error(f"Error in check_membership: {str(e)}")
        await query.message.reply_text(f"خطایی رخ داد: {str(e)}")

# اضافه کردن هندلرها
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(check_membership, pattern="check_membership"))

# مسیر Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        logger.info("Received webhook update")
        update = Update.de_json(request.get_json(force=True), bot_app.bot)
        if update:
            # استفاده از run_async برای پردازش آپدیت‌ها
            loop = asyncio.get_event_loop()
            loop.run_until_complete(bot_app.process_update(update))
            logger.info("Update processed successfully")
            return "OK", 200
        else:
            logger.error("No update received")
            return "No update", 400
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return "Error", 500

# تنظیم Webhook موقع شروع سرور
@app.route("/")
def set_webhook():
    try:
        webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
        loop = asyncio.get_event_loop()
        loop.run_until_complete(bot_app.bot.set_webhook(webhook_url))
        logger.info(f"Webhook set to {webhook_url}")
        return "Webhook set successfully", 200
    except Exception as e:
        logger.error(f"Failed to set webhook: {str(e)}")
        return f"Failed to set webhook: {str(e)}", 500

# اجرای سرور
if __name__ == "__main__":
    port = int(os.getenv("PORT", 80))
    logger.info(f"Starting Flask server on port {port}")
    # راه‌اندازی سرور Flask
    app.run(host="0.0.0.0", port=port, debug=False)
