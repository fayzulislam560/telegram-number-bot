import pandas as pd
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Bot Token
TOKEN = "8373131918:AAE3imgCIDMUjugfd8XErKXjQuYbfoUBkwc"

numbers = []
index = 0

def start(update, context):
    update.message.reply_text(
        "ফাইল পাঠান (xlsx বা txt)। তারপর 'Get New Number' চাপুন।"
    )

def handle_file(update, context):
    global numbers, index
    file = update.message.document.get_file()
    file_path = file.download()

    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            numbers = [line.strip() for line in f if line.strip()]
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path, header=None)
        numbers = df[0].astype(str).tolist()

    index = 0

    keyboard = [[InlineKeyboardButton("📱 Get New Number", callback_data="getnum")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        f"ফাইল লোড হয়েছে! মোট {len(numbers)} নাম্বার।",
        reply_markup=reply_markup
    )

def get_number(update, context):
    global index, numbers
    query = update.callback_query

    if index < len(numbers):
        next_num = numbers[index]
        index += 1
        query.answer()
        query.edit_message_text(f"📞 Number: `{next_num}`", parse_mode="Markdown")
    else:
        query.answer()
        query.edit_message_text("✔️ সব নাম্বার শেষ। নতুন ফাইল দিন।")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, handle_file))
    dp.add_handler(CallbackQueryHandler(get_number, pattern="getnum"))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
