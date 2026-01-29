import telebot
from telebot import types

TOKEN = '8587792984:AAG0k7OU93P1-W72pleShz8QMt6T4gnFnPU'
bot = telebot.TeleBot(TOKEN)

# Вставь сюда свою ссылку из GitHub Pages
APP_URL = "https://negrik-na-polyah.github.io/tg-app-1/"

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Важно: URL должен вести на твой index.html на GitHub Pages
    web_app = types.WebAppInfo(url=APP_URL)
    
    btn = types.KeyboardButton(text="Запустить приложение 🚀", web_app=web_app)
    markup.add(btn)
    
    bot.send_message(message.chat.id, "Нажми на кнопку ниже, чтобы открыть Mini App:", reply_markup=markup)

@bot.message_handler(content_types=['web_app_data'])
def handle_app_data(message):
    bot.send_message(message.chat.id, f"Приложение прислало: {message.web_app_data.data}")

bot.infinity_polling()