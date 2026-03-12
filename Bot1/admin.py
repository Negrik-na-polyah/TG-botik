import telebot
from config import ADMIN_IDS
from database import get_connection


# состояния админа
admin_states = {}


def is_admin(user_id):
    if user_id in ADMIN_IDS:
        print(f"✅ Админ {user_id} использует панель")
        return True

    print(f"❌ Пользователь {user_id} попытался открыть админку")
    return False


def register(bot):

    # -----------------------
    # Админ панель
    # -----------------------
    @bot.message_handler(commands=["admin"])
    def admin_panel(message):

        if not is_admin(message.from_user.id):
            bot.send_message(message.chat.id, "⛔ Нет доступа")
            return

        markup = telebot.types.InlineKeyboardMarkup()

        markup.add(
            telebot.types.InlineKeyboardButton(
                "➕ Добавить товар",
                callback_data="admin_add"
            )
        )

        markup.add(
            telebot.types.InlineKeyboardButton(
                "🗑 Удалить товар",
                callback_data="admin_delete"
            )
        )

        markup.add(
            telebot.types.InlineKeyboardButton(
                "📦 Заказы",
                callback_data="admin_orders"
            )
        )

        markup.add(
            telebot.types.InlineKeyboardButton(
                "📊 Статистика",
                callback_data="admin_stats"
            )
        )

        bot.send_message(
            message.chat.id,
            "👑 Админ панель",
            reply_markup=markup
        )

    # -----------------------
    # Получение photo_id
    # -----------------------
    @bot.message_handler(content_types=["photo"])
    def get_photo(message):

        user_id = message.from_user.id

        if not is_admin(user_id):
            return

        photo_id = message.photo[-1].file_id

        bot.send_message(
            message.chat.id,
            f"📷 ID фото:\n`{photo_id}`",
            parse_mode="Markdown"
        )

        print("📷 Photo ID:", photo_id)

        # если админ добавляет товар
        if user_id in admin_states and admin_states[user_id]["step"] == "photo":

            admin_states[user_id]["photo"] = photo_id
            admin_states[user_id]["step"] = "name"

            bot.send_message(
                message.chat.id,
                "Введите название товара"
            )

    # -----------------------
    # Добавить товар
    # -----------------------
    @bot.callback_query_handler(func=lambda call: call.data == "admin_add")
    def add_product(call):

        if not is_admin(call.from_user.id):
            return

        admin_states[call.from_user.id] = {"step": "photo"}

        bot.send_message(
            call.message.chat.id,
            "📷 Отправьте фото товара"
        )

    # -----------------------
    # Обработка текста
    # -----------------------
    @bot.message_handler(func=lambda message: message.from_user.id in admin_states)
    def add_product_steps(message):

        state = admin_states[message.from_user.id]

        if state["step"] == "name":

            state["name"] = message.text
            state["step"] = "description"

            bot.send_message(
                message.chat.id,
                "Введите описание"
            )

        elif state["step"] == "description":

            state["description"] = message.text
            state["step"] = "price"

            bot.send_message(
                message.chat.id,
                "Введите цену"
            )

        elif state["step"] == "price":

            try:
                state["price"] = int(message.text)
            except:
                bot.send_message(message.chat.id, "Цена должна быть числом")
                return

            state["step"] = "category"

            bot.send_message(
                message.chat.id,
                "Введите категорию:\n\nzodiac\nbears\nducks\ncustom"
            )

        elif state["step"] == "category":

            state["category"] = message.text

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO products
            (name,description,price,category,photo)
            VALUES (?,?,?,?,?)
            """,(
                state["name"],
                state["description"],
                state["price"],
                state["category"],
                state["photo"]
            ))

            conn.commit()
            conn.close()

            bot.send_message(
                message.chat.id,
                "✅ Товар успешно добавлен"
            )

            print("📦 Добавлен товар:", state["name"])

            del admin_states[message.from_user.id]

    # -----------------------
    # Удаление товара
    # -----------------------
    @bot.callback_query_handler(func=lambda call: call.data == "admin_delete")
    def delete_product(call):

        if not is_admin(call.from_user.id):
            return

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id,name FROM products")

        products = cursor.fetchall()

        conn.close()

        markup = telebot.types.InlineKeyboardMarkup()

        for product in products:

            markup.add(
                telebot.types.InlineKeyboardButton(
                    f"❌ {product[1]}",
                    callback_data=f"delete:{product[0]}"
                )
            )

        bot.send_message(
            call.message.chat.id,
            "Выберите товар для удаления",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("delete:"))
    def confirm_delete(call):

        product_id = call.data.split(":")[1]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM products WHERE id=?",
            (product_id,)
        )

        conn.commit()
        conn.close()

        bot.send_message(
            call.message.chat.id,
            "🗑 Товар удален"
        )

        print("🗑 Удален товар ID:", product_id)

    # -----------------------
    # Заказы
    # -----------------------
    @bot.callback_query_handler(func=lambda call: call.data == "admin_orders")
    def show_orders(call):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT orders.id, products.name, orders.quantity, orders.price
        FROM orders
        JOIN products ON products.id = orders.product_id
        """)

        orders = cursor.fetchall()

        conn.close()

        if not orders:

            bot.send_message(
                call.message.chat.id,
                "📦 Заказов пока нет"
            )
            return

        text = "📦 Список заказов\n\n"

        for order in orders:

            text += f"""
№{order[0]}
Товар: {order[1]}
Количество: {order[2]}
Сумма: {order[3]} руб

"""

        bot.send_message(
            call.message.chat.id,
            text
        )

    # -----------------------
    # Статистика
    # -----------------------
    @bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
    def stats(call):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(price) FROM orders")
        revenue = cursor.fetchone()[0]

        conn.close()

        bot.send_message(
            call.message.chat.id,
            f"""
📊 Статистика

Всего заказов: {total_orders}
Выручка: {revenue if revenue else 0} руб
"""
        )