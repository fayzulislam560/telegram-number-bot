import os
import re
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

TOKEN = os.getenv("TOKEN")

user_numbers = {}
current_index = {}

# Extract numbers and always add +
def extract_numbers_from_dataframe(df):
    numbers = []
    for _, row in df.iterrows():
        for cell in row:
            # যদি cell string হয়
            if isinstance(cell, str):
                nums = re.findall(r'\d{8,15}', cell)
                for n in nums:
                    if not n.startswith("+"):
                        n = "+" + n
                    numbers.append(n)

            # যদি cell সংখ্যা হয় (int/float)
            elif isinstance(cell, (int, float)):
                n = str(int(cell))
                if not n.startswith("+"):
                    n = "+" + n
                numbers.append(n)

    return numbers

def start(update: Update, context: CallbackContext):
    update.message.reply_text("📄 আপনার TXT বা XLSX ফাইল পাঠান।")

def receive_file(update: Update, context: CallbackContext):
    file = update.message.document
    file_path = file.get_file().download()

    try:
        if file.file_name.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path, header=None, sep="\n")

        numbers = extract_numbers_from_dataframe(df)
        user_id = update.message.from_user.id

        if len(numbers) == 0:
            update.message.reply_text("❌ কোন নাম্বার পাওয়া যায়নি।")
            return

        user_numbers[user_id] = numbers
        current_index[user_id] = 0

        update.message.reply_text(
            f"✔️ মোট {len(numbers)} টি নাম্বার পাওয়া গেছে!\n\nপরবর্তী নাম্বার পেতে বাটন চাপুন:",
            reply_markup=get_button()
        )

    except Exception as e:
        update.message.reply_text(f"❌ ফাইল রিড করতে সমস্যা:\n{str(e)}")

def get_button():
    keyboard = [
        [InlineKeyboardButton("📞 Get New Number", callback_data="get_number")]
    ]
    return InlineKeyboardMarkup(keyboard)

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    user_id = query.from_user.id

    if user_id not in user_numbers:
        query.edit_message_text("❌ আগে ফাইল পাঠান।")
        return

    index = current_index[user_id]
    numbers = user_numbers[user_id]

    if index >= len(numbers):
        query.edit_message_text("✔️ সব নাম্বার শেষ।")
        return

    number = numbers[index]
    current_index[user_id] += 1

    query.edit_message_text(
        f"📱 আপনার নাম্বার:\n\n`{number}`\n\nNext পেতে আবার বাটন চাপুন।",
        parse_mode="Markdown",
        reply_markup=get_button()
    )

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, receive_file))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
