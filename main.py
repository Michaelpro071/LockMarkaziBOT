import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# تنظیم لاگ‌گذاری برای دیباگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# تنظیم توکن و آیدی کانال
TOKEN = os.getenv("TELEGRAM_TOKEN", "5605657176:AAFKyDSvc1j_nV5RRHX91lJDGCZzpU9es4I")
CHANNEL_ID = "@RoyalGuardX"  # یوزرنیم کانالت (مثلاً @MyChannel)

# ایجاد اپلیکیشن Flask
app = Flask(__name__)

# ایجاد اپلیکیشن تلگرام
bot_app = Application.builder().token(TOKEN).build()

# تابع برای دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        logger.info(f"Processing /start command for user {user.id}")
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
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        await update.message.reply_text(f"خطایی رخ داد: {str(e)}")

# تابع برای بررسی عضویت
async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    try:
        logger.info(f"Checking membership for user {user.id}")
        # بررسی دوباره عضویت
        member = await context.bot.get_chat_member(CHANNEL_ID, user.id)
        if member.status in ["member", "administrator", "creator"]:
            await query.message.reply_text("تبریک! حالا شما عضو کانال هستید!")
        else:
            await query.message.reply_text("شما هنوز عضو کانال نشدید. لطفاً در کانال عضو بشید.")
    except Exception as e:
        logger.error(f"Error in check_membership: {str(e)}")
        await query.message.reply_text(f"خطایی رخ داد: {str(e)}")

# اضافه کردن هندلرها به ربات
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(check_membership, pattern="check_membership"))

# مسیر Webhook در Flask
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    try:
        logger.info("Received webhook update")
        # دریافت آپدیت از تلگرام
        json_data = request.get_json(force=True)
        if not json_data:
            logger.warning("No JSON data received")
            return "No JSON data", 400
        update = Update.de_json(json_data, bot_app.bot)
        if not update:
            logger.warning("Invalid update received")
            return "Invalid update", 400
        # پردازش آپدیت
        await bot_app.process_update(update)
        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return f"Error: {str(e)}", 500

# تنظیم Webhook موقع شروع سرور
@app.route("/")
async def set_webhook():
    try:
        webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
        logger.info(f"Setting webhook to {webhook_url}")
        await bot_app.bot.set_webhook(webhook_url)
        return "Webhook set successfully", 200
    except Exception as e:
        logger.error(f"Failed to set webhook: {str(e)}")
        return f"Failed to set webhook: {str(e)}", 500

# تابع برای اجرای اولیه اپلیکیشن
async def init_bot():
    try:
        webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
        logger.info(f"Initializing bot with webhook: {webhook_url}")
        await bot_app.bot.set_webhook(webhook_url)
    except Exception as e:
        logger.error(f"Failed to initialize bot: {str(e)}")

if __name__ == "__main__":
    # اجرای اپلیکیشن Flask
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting Flask app on port {port}")
    # اجرای اولیه Webhook
    asyncio.run(init_bot())
    # اجرای سرور Flask
    app.run(host="0.0.0.0", port=port)
