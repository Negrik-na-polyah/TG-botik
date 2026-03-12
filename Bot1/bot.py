import telebot
import logging

from config import BOT_TOKEN
from database import init_db,seed_products

import catalog
import orders
import admin

logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
def start(message): 

    markup = telebot.types.InlineKeyboardMarkup()

    markup.add(
        telebot.types.InlineKeyboardButton(
            "🧸 Каталог",
            callback_data="catalog"
        )
    )

    markup.add(
        telebot.types.InlineKeyboardButton(
            "🚚 Доставка",
            callback_data="delivery"
        )
    )

    markup.add(
        telebot.types.InlineKeyboardButton(
            "❓ Помощь",
            callback_data="help"
        )
    )

    bot.send_message(
        message.chat.id,
        "Добро пожаловать в магазин мягких игрушек 🧸",
        reply_markup=markup
    )


def main():

    print("Bot started")

    init_db()
    seed_products()

    catalog.register(bot)
    orders.register(bot)
    admin.register(bot)

    bot.infinity_polling()


if __name__ == "__main__":
    main()