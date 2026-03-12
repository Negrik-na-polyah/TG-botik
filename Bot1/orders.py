import logging

import telebot
from config import ADMIN_IDS
from database import get_connection

logger = logging.getLogger(__name__)

# Состояния пользователей при оформлении заказа
# { user_id: { step, product_id, quantity, name, phone, address } }
user_states = {}


def notify_admins(bot, text):
    """Отправить уведомление всем админам."""
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, text)
        except Exception as e:
            logger.warning("Не удалось уведомить админа %s: %s", admin_id, e)


def register(bot):

    # -----------------------
    # Шаг 1: нажали "Купить"
    # -----------------------
    @bot.callback_query_handler(func=lambda call: call.data.startswith("buy:"))
    def buy_start(call):

        product_id = int(call.data.split(":")[1])
        user_id = call.from_user.id

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, price FROM products WHERE id=?", (product_id,))
            product = cursor.fetchone()

        if not product:
            bot.send_message(call.message.chat.id, "❌ Товар не найден")
            return

        user_states[user_id] = {
            "step": "quantity",
            "product_id": product_id,
            "product_name": product[0],
            "product_price": product[1],
        }

        bot.send_message(
            call.message.chat.id,
            f"🛒 Вы выбрали: *{product[0]}*\n"
            f"💰 Цена: {product[1]} руб\n\n"
            f"Введите количество:",
            parse_mode="Markdown"
        )

    # -----------------------
    # Шаг 2–4: сбор данных
    # -----------------------
    @bot.message_handler(func=lambda message: message.from_user.id in user_states)
    def order_steps(message):

        user_id = message.from_user.id
        state = user_states[user_id]
        step = state["step"]

        # --- Количество ---
        if step == "quantity":

            try:
                quantity = int(message.text)
                if quantity <= 0:
                    raise ValueError
            except ValueError:
                bot.send_message(message.chat.id, "⚠️ Введите целое число больше нуля")
                return

            state["quantity"] = quantity
            state["step"] = "name"

            total = state["product_price"] * quantity
            state["total"] = total

            bot.send_message(
                message.chat.id,
                f"✅ Количество: {quantity} шт.\n"
                f"💰 Итого: {total} руб\n\n"
                f"Введите ваше имя и фамилию:"
            )

        # --- Имя ---
        elif step == "name":

            state["name"] = message.text.strip()
            state["step"] = "phone"

            bot.send_message(
                message.chat.id,
                "📞 Введите ваш номер телефона:"
            )

        # --- Телефон ---
        elif step == "phone":

            phone = message.text.strip()

            if len(phone) < 7:
                bot.send_message(message.chat.id, "⚠️ Введите корректный номер телефона")
                return

            state["phone"] = phone
            state["step"] = "address"

            bot.send_message(
                message.chat.id,
                "📍 Введите адрес доставки:"
            )

        # --- Адрес → создаём заказ ---
        elif step == "address":

            state["address"] = message.text.strip()

            # Сохраняем заказ в БД
            with get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                INSERT INTO orders (user_id, product_id, quantity, price, name, phone, address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    state["product_id"],
                    state["quantity"],
                    state["total"],
                    state["name"],
                    state["phone"],
                    state["address"],
                ))

                order_id = cursor.lastrowid

            # Подтверждение пользователю
            bot.send_message(
                message.chat.id,
                f"✅ *Заказ №{order_id} оформлен!*\n\n"
                f"🧸 Товар: {state['product_name']}\n"
                f"📦 Количество: {state['quantity']} шт.\n"
                f"💰 Сумма: {state['total']} руб\n"
                f"👤 Имя: {state['name']}\n"
                f"📞 Телефон: {state['phone']}\n"
                f"📍 Адрес: {state['address']}\n\n"
                f"Мы свяжемся с вами для подтверждения 🤝",
                parse_mode="Markdown"
            )

            # Уведомление админам
            notify_admins(
                bot,
                f"🛍 *Новый заказ №{order_id}*\n\n"
                f"🧸 Товар: {state['product_name']}\n"
                f"📦 Количество: {state['quantity']} шт.\n"
                f"💰 Сумма: {state['total']} руб\n"
                f"👤 Имя: {state['name']}\n"
                f"📞 Телефон: {state['phone']}\n"
                f"📍 Адрес: {state['address']}\n"
                f"🆔 User ID: {user_id}"
            )

            logger.info("✅ Новый заказ №%s от %s", order_id, user_id)

            del user_states[user_id]
