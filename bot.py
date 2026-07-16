import os
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

# Put your Telegram Bot Token here
TOKEN = "8744677134:AAFgbdvbt1WkuPD47bsRJzxLe52OJphTseE"

# 1. Welcome Message Function
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        # Don't welcome the bot itself
        if member.id == context.bot.id:
            continue
            
        first_name = member.first_name
        welcome_text = f"ሰላም {first_name} 👋\nእንኳን ወደ የለኩ ከታ ቃለህይወት ቤተክርስቲያን የወጣቶች አገልግሎት ግሩፓችን በደህና መጣህ/ሽ! ✨"
        
        await update.message.reply_text(welcome_text)

# 2. Link Deletion Function (Ignores Admins)
async def delete_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    chat_id = message.chat_id
    user_id = message.from_user.id

    try:
        # Check if the user is an Admin or Creator
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status in ['administrator', 'creator']:
            return  # Allow admins to send links
    except Exception as e:
        print(f"Error checking admin status: {e}")

    # Delete the message if it contains links
    await message.delete()

def main():
    keep_alive()

    application = Application.builder().token(TOKEN).build()

    # Welcome message handler for new group members
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

    # Link filter handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & (filters.Entity("url") | filters.Entity("text_link")), delete_links))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
