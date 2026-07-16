import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Flask setup for Render keep-alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

TOKEN = "8744677134:AAFgbdvbt1WkuPD47bsRJzxLe52OJphTseE"

# 1. Welcome Message Function
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            continue
            
        first_name = member.first_name
        welcome_text = f"ሰላም {first_name} 👋\nእንኳን ወደ የለኩ ከታ ቃለህይወት ቤተክርስቲያን የወጣቶች አገልግሎት ግሩፓችን በደህና መጣህ/ሽ! ✨"
        
        await update.message.reply_text(welcome_text)

# Helper function to delete warning message after a delay
async def delete_warning_after_delay(chat_id, message_id, context, delay=5):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"Error deleting warning message: {e}")

# 2. Link Deletion + Warning Message Function
async def delete_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    chat_id = message.chat_id
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    try:
        # Check if user is Admin or Creator
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status in ['administrator', 'creator']:
            return  # Admins can send links
    except Exception as e:
        print(f"Error checking admin status: {e}")

    try:
        # 1. Delete the link message
        await message.delete()
        
        # 2. Send warning text
        warning_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"⚠️ ሰላም {user_name}፣ በዚህ ግሩፕ ውስጥ ሊንክ መላክ የተከለከለ ነው! ጌታ ይባርክ/ሽ"
        )
        
        # 3. Auto-delete the warning message after 5 seconds to keep chat clean
        asyncio.create_task(delete_warning_after_delay(chat_id, warning_msg.message_id, context, 5))
        
    except Exception as e:
        print(f"Error handling link deletion: {e}")

def main():
    keep_alive()

    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    application.add_handler(MessageHandler(filters.TEXT & (filters.Entity("url") | filters.Entity("text_link")), delete_links))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
