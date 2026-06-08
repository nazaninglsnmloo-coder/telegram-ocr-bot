import telebot
import requests
from flask import Flask
from threading import Thread
import os
import time

TOKEN = "8933923406:AAHdsIDIrxMM08fnDnHtg3pjhWroYec2zXA"
OCR_API_KEY = "K80984775388957"  # کلید رایگان OCR.space
OCR_URL = "https://api.ocr.space/parse/image"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "📄 به ربات تبدیل عکس و PDF به متن خوش اومدی!\n\nعکس یا فایل اسکن شده بفرست تا متنش رو واست پیدا کنم.")

@bot.message_handler(content_types=['photo'])
def handle_photo(msg):
    try:
        bot.reply_to(msg, "📸 عکس دریافت شد. در حال پردازش...")

        file_info = bot.get_file(msg.photo[-1].file_id)
        file = bot.download_file(file_info.file_path)

        files = {'file': ('image.jpg', file, 'image/jpeg')}
        data = {'apikey': OCR_API_KEY, 'language': 'eng+per'}

        response = requests.post(OCR_URL, files=files, data=data)
        result = response.json()

        if result.get("IsErroredOnProcessing"):
            bot.reply_to(msg, "❌ نتونستم متن رو تشخیص بدم. عکس واضح‌تری بفرست.")
            return

        parsed_text = result.get("ParsedResults", [{}])[0].get("ParsedText", "")

        if parsed_text.strip():
            if len(parsed_text) > 4000:
                with open("output.txt", "w", encoding="utf-8") as f:
                    f.write(parsed_text)
                with open("output.txt", "rb") as f:
                    bot.send_document(msg.chat.id, f, caption="📝 متن کامل (به دلیل طولانی بودن فایل شد)")
            else:
                bot.reply_to(msg, f"📝 **متن پیدا شده:**\n\n{parsed_text}\n\n✅ این متن قابل کپی و جستجوست.")
        else:
            bot.reply_to(msg, "❌ توی این عکس متنی پیدا نشد.")
    except Exception as e:
        bot.reply_to(msg, f"❌ خطا: {e}")

@bot.message_handler(content_types=['document'])
def handle_doc(msg):
    try:
        bot.reply_to(msg, "📄 فایل دریافت شد. در حال پردازش...")

        file_info = bot.get_file(msg.document.file_id)
        file = bot.download_file(file_info.file_path)

        files = {'file': ('file.pdf', file, 'application/pdf')}
        data = {'apikey': OCR_API_KEY, 'language': 'eng+per'}

        response = requests.post(OCR_URL, files=files, data=data)
        result = response.json()

        if result.get("IsErroredOnProcessing"):
            bot.reply_to(msg, "❌ نتونستم متن رو تشخیص بدم. مطمئن شو فایل اسکن شده باشه و کیفیت خوبی داشته باشه.")
            return

        parsed_text = result.get("ParsedResults", [{}])[0].get("ParsedText", "")

        if parsed_text.strip():
            if len(parsed_text) > 4000:
                with open("output.txt", "w", encoding="utf-8") as f:
                    f.write(parsed_text)
                with open("output.txt", "rb") as f:
                    bot.send_document(msg.chat.id, f, caption="📝 متن کامل فایل (قابل کپی و جستجو)")
            else:
                bot.reply_to(msg, f"📝 **متن پیدا شده:**\n\n{parsed_text}\n\n✅ این متن قابل کپی و جستجوست.")
        else:
            bot.reply_to(msg, "❌ توی این فایل متنی پیدا نشد.")
    except Exception as e:
        bot.reply_to(msg, f"❌ خطا: {e}")

@bot.message_handler(func=lambda msg: True)
def unknown(msg):
    bot.reply_to(msg, "❓ دستور نامعتبر!\n\nبرای راهنما /start رو بفرست.")

@app.route('/')
def home():
    return "ربات روشنه!", 200

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    while True:
        try:
            print("ربات در حال اجراست...")
            bot.infinity_polling()
        except Exception as e:
            print(f"خطا: {e}")
            time.sleep(5)

if __name__ == "__main__":
    bot_thread = Thread(target=run_bot)
    bot_thread.start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)