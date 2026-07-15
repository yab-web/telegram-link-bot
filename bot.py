import logging
import re
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# የቦትህን Token እዚህ ጋር አስገባ
BOT_TOKEN = "8744677134:AAHlh_vL89B8OVEOEJcitb1cYxOpJ_LbKAg"

# ሎግ ለመከታተል (ለመቆጣጠር)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def check_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    # ቦቱ በግሩፕ ውስጥ ብቻ እንዲሰራ (በግል እንዳይሆን)
    if chat.type in ["group", "supergroup"]:
        
        # ላኪው የግሩፑ አስተዳዳሪ (Admin) ከሆነ ሊንክ መላክ ይችላል
        member = await chat.get_member(user.id)
        if member.status in ["creator", "administrator"]:
            return

        text = message.text or message.caption or ""
        
        # ሊንክ መኖሩን በረቂቅ መፈትሻ (Regular Expression) ማረጋገጫ
        # http://, https://, t.me, ወይም .com/.org የመሳሰሉትን ይይዛል
        link_pattern = re.compile(
            r'(https?://[^\s]+)|(www\.[^\s]+)|([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
        )

        if link_pattern.search(text):
            try:
                # 1. የተላከውን ሊንክ ማጥፋት
                await message.delete()
                
                # 2. ለላከው ሰው ብቻ የሚታይ ማስጠንቀቂያ መላክ (ለ5 ሰከንድ ቆይቶ የሚጠፋ)
                warning_text = f"🚫 @{user.username or user.first_name}፣ በዚህ ግሩፕ ውስጥ ሊንክ ማስተላለፍ ወይም መልቀቅ አይችሉም!"
                warning_msg = await context.bot.send_message(
                    chat_id=chat.id, 
                    text=warning_text
                )
                
                # ግሩፑ በሜሴጅ እንዳይጨናነቅ ማስጠንቀቂያውን ከጥቂት ሰከንዶች በኋላ ማጥፋት (አማራጭ)
                context.job_queue.run_once(
                    delete_warning, 
                    5, 
                    data={"chat_id": chat.id, "message_id": warning_msg.message_id}
                )
                
            except Exception as e:
                logging.error(f"ስህተት ተከስቷል: {e}")

# ማስጠንቀቂያውን የሚያጠፋው ተግባር
async def delete_warning(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    try:
        await context.bot.delete_message(
            chat_id=job.data["chat_id"], 
            message_id=job.data["message_id"]
        )
    except Exception:
        pass

def main():
    # ቦቱን ማስነሳት
    application = Application.builder().token(BOT_TOKEN).build()

    # ሁሉንም ጽሁፎች የሚፈትሽ (የሊንክ ማጣሪያን ጨምሮ)
    application.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, check_links))

    # ቦቱን በቋሚነት ማሰራት
    print("ቦቱ መስራት ጀምሯል...")
    application.run_polling()

if __name__ == '__main__':
    main()