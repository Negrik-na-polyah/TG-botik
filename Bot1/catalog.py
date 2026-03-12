import telebot
from database import get_connection


def register(bot):

    @bot.callback_query_handler(func=lambda call: call.data == "catalog")
    def show_categories(call):

        markup = telebot.types.InlineKeyboardMarkup()

        markup.add(
            telebot.types.InlineKeyboardButton("♈ Знаки зодиака",callback_data="category:zodiac")
        )

        markup.add(
            telebot.types.InlineKeyboardButton("🧸 Мишки",callback_data="category:bears")
        )

        markup.add(
            telebot.types.InlineKeyboardButton("🦆 Уточки",callback_data="category:ducks")
        )

        markup.add(
            telebot.types.InlineKeyboardButton("🎨 Кастомная игрушка",callback_data="category:custom")
        )

        bot.edit_message_text(
            "Выберите категорию:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )


    @bot.callback_query_handler(func=lambda call: call.data.startswith("category"))
    def show_products(call):

        category = call.data.split(":")[1]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id,name FROM products WHERE category=?",
            (category,)
        )

        products = cursor.fetchall()

        markup = telebot.types.InlineKeyboardMarkup()

        for product in products:
            markup.add(
                telebot.types.InlineKeyboardButton(
                    product[1],
                    callback_data=f"product:{product[0]}"
                )
            )

        markup.add(
            telebot.types.InlineKeyboardButton(
                "⬅ Назад",
                callback_data="catalog"
            )
        )

        bot.edit_message_text(
            "Товары:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )


    @bot.callback_query_handler(func=lambda call: call.data.startswith("product"))
    def product_page(call):

        product_id = call.data.split(":")[1]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name,description,price,photo,category FROM products WHERE id=?",
            (product_id,)
        )

        name,description,price,photo,category = cursor.fetchone()

        text=f"""
🧸 {name}

{description}

💰 Цена: {price} руб
"""

        markup = telebot.types.InlineKeyboardMarkup()

        markup.add(
            telebot.types.InlineKeyboardButton(
                "🛒 Купить",
                callback_data=f"buy:{product_id}"
            )
        )

        markup.add(
            telebot.types.InlineKeyboardButton(
                "⬅ Назад",
                callback_data=f"category:{category}"
            )
        )

        bot.send_photo(
            call.message.chat.id,
            photo,
            caption=text,
            reply_markup=markup
        )