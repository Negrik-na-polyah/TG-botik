import telebot
from telebot import types

TOKEN = '8587792984:AAG0k70U93Pl-W72pleShz8QMt6T4gnFnPU'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, f"hi, {message.from_user.first_name}!")

bot.infinity_polling()