import os
import re
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. Web Server for Render Keep-Alive ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running live!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- 2. Telegram Bot Setup ---
TOKEN = "8744677134:AAH1h_vL89B80VE0EJcitb1cYx0pJ_LbKAg"

# Regex pattern for URLs
URL_REGEX = r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.[a-zA-Z]{2,}[^\s]*)'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ቦቱ በስኬት ስራ ጀምሯል! ሊንኮችን በራስ-ሰር ያጠፋል።")

async def delete_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    # Check if user is Admin or Creator (Allow admins to post links)
    member = await context.bot.get_chat_member(chat_id=message.chat_id, user_id=message.from_user.id)
    if member.status in ['administrator', 'creator']:
        return

    # Check for links
    if re.search(URL_REGEX, message.text):
        try:
            await message.delete()
            print(f"Deleted link from user: {message.from_user.username or message.from_user.first_name}")
            await message.chat.send_message(
                f"⚠️ ተጠቃሚ @{message.from_user.username or message.from_user.first_name}፣ በግሩፑ ውስጥ ሊንክ መላክ የተከለከለ ነው!"
            )
        except Exception as e:
            print(f"Error deleting message: {e}")

def main():
    keep_alive()  # Starts the web server
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, delete_links))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
