import logging

import telebot
from config import ADMIN_IDS
from database import get_connection

logger = logging.getLogger(__name__)

# состояния админа
admin_states = {}


def is_admin(user_id):
    if user_id in ADMIN_IDS:
        logger.info("✅ Админ %s использует панель", user_id)
        return True

    logger.warning("❌ Пользователь %s попытался открыть админку", user_id)
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
            except Exception:
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
            """, (
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
        SELECT orders.id, products.name, orders.quantity, orders.price,
               orders.name, orders.phone, orders.address, orders.created_at
        FROM orders
        JOIN products ON products.id = orders.product_id
        ORDER BY orders.id DESC
        """)

        orders = cursor.fetchall()

        conn.close()

        if not orders:

            bot.send_message(
                call.message.chat.id,
                "📦 Заказов пока нет"
            )
            return

        text = "📦 *Список заказов*\n\n"

        for order in orders:

            text += (
                f"*№{order[0]}* | {order[7][:10]}\n"
                f"Товар: {order[1]}\n"
                f"Кол-во: {order[2]} шт. | Сумма: {order[3]} руб\n"
                f"Клиент: {order[4]}\n"
                f"Тел: {order[5]}\n"
                f"Адрес: {order[6]}\n"
                f"{'─' * 28}\n"
            )

        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode="Markdown"
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

        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]

        cursor.execute("""
        SELECT products.name, SUM(orders.quantity) as cnt
        FROM orders
        JOIN products ON products.id = orders.product_id
        GROUP BY products.name
        ORDER BY cnt DESC
        LIMIT 3
        """)
        top = cursor.fetchall()

        conn.close()

        top_text = ""
        for i, item in enumerate(top, 1):
            top_text += f"  {i}. {item[0]} — {item[1]} шт.\n"

        bot.send_message(
            call.message.chat.id,
            f"📊 *Статистика магазина*\n\n"
            f"📦 Всего заказов: {total_orders}\n"
            f"💰 Выручка: {revenue if revenue else 0} руб\n"
            f"🧸 Товаров в каталоге: {total_products}\n\n"
            f"🏆 Топ товаров:\n{top_text if top_text else '  Нет данных'}",
            parse_mode="Markdown"
        )
