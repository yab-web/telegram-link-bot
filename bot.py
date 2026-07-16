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
TOKEN = "8744677134:AAElm8oHWSO21CUP5G5YjmjCdk5mQ5bJDHI"

# Regex pattern for URLs
URL_REGEX = r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.[a-zA-Z]{2,}[^\s]*)'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ቦቱ በስኬት ስራ ጀምሯል! ሊንኮችን በራስ-ሰር ያጠፋል።")

async def delete_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # Check text or caption for links
    text_content = message.text or message.caption or ""

    # Check if user is Admin or Creator (Allow admins to post links)
    member = await context.bot.get_chat_member(chat_id=message.chat_id, user_id=message.from_user.id)
    if member.status in ['administrator', 'creator']:
        return

    # Check for links or link entities
    has_link_entity = any(entity.type in ['url', 'text_link'] for entity in (message.entities or []))
    
    if re.search(URL_REGEX, text_content) or has_link_entity:
        try:
            await message.delete()
            
            user_info = message.from_user.username or message.from_user.first_name
            print(f"Deleted link from user: {user_info}")
            
            await message.chat.send_message(
                f"⚠️ ተጠቃሚ @{user_info}፣ በግሩፑ ውስጥ ሊንክ መላክ የተከለከለ ነው!"
            )
        except Exception as e:
            print(f"Error deleting message: {e}")

def main():
    keep_alive()  # Starts the web server
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    
    # ፕሪቪው ያላቸውን እና መደበኛ ሊንኮችን ሙሉ በሙሉ የሚይዝ መያዣ
    link_filter = (filters.TEXT | filters.Entity("url") | filters.Entity("text_link")) & ~filters.COMMAND
    application.add_handler(MessageHandler(link_filter, delete_links))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
