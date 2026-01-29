import telebot
from telebot import types

TOKEN = '8587792984:AAG0k70U93Pl-W72pleShz8QMt6T4gnFnPU'
bot = telebot.TeleBot(TOKEN)

# Не забывай менять ?v=... чтобы обновлялось!
APP_URL = "https://negrik-na-polyah.github.io/TG-botik/?v=test999"

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # ВАЖНО: открываем только через KeyboardButton
    web_app = types.WebAppInfo(url=APP_URL)
    btn = types.KeyboardButton(text="Играть в Кликер 🎮", web_app=web_app)
    markup.add(btn)
    bot.send_message(message.chat.id, "Нажми на кнопку ниже, чтобы начать игру:", reply_markup=markup)

@bot.message_handler(content_types=['web_app_data'])
def handle_data(message):
    # Получаем наше число кликов
    score = message.web_app_data.data
    bot.send_message(message.chat.id, f"🏆 Твой результат сохранен! Ты накликал: {score}")

bot.infinity_polling()