user_states = {}


def register(bot):

    @bot.callback_query_handler(func=lambda call: call.data.startswith("product"))
    def product_page(call):

        product_id = int(call.data.split(":")[1])

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT name, description, price FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()

        text = f"""
{product[0]}

{product[1]}

Цена: {product[2]} руб
"""

        markup = telebot.types.InlineKeyboardMarkup()

        markup.add(
            telebot.types.InlineKeyboardButton(
                "Купить",
                callback_data=f"buy:{product_id}"
            )
        )

        bot.send_message(call.message.chat.id, text, reply_markup=markup)