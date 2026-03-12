import time

import telebot
import logging

from config import BOT_TOKEN
from database import init_db, seed_products

import catalog
import orders
import admin

logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(BOT_TOKEN)


def build_main_menu_markup():
    """Build markup for the main bot menu."""

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("🧸 Каталог", callback_data="catalog"),
        telebot.types.InlineKeyboardButton("🚚 Доставка", callback_data="delivery"),
        telebot.types.InlineKeyboardButton("❓ Помощь", callback_data="help"),
    )

    return markup


def build_back_markup():
    """Build a simple back-to-main-menu button markup."""

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_main")
    )
    return markup


# -----------------------
# /start
# -----------------------
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Добро пожаловать в магазин мягких игрушек 🧸\n\n"
        "Выберите раздел:",
        reply_markup=build_main_menu_markup(),
    )


# -----------------------
# Доставка
# -----------------------
@bot.callback_query_handler(func=lambda call: call.data == "delivery")
def delivery(call):

    bot.edit_message_text(
        "🚚 *Информация о доставке*\n\n"
        "📦 Доставляем по всей России\n\n"
        "🏙 Курьером по Москве и МО:\n"
        "  • Срок: 1–2 дня\n"
        "  • Стоимость: 300 руб (бесплатно от 2000 руб)\n\n"
        "🌍 Почтой России по РФ:\n"
        "  • Срок: 3–10 дней\n"
        "  • Стоимость: от 250 руб\n\n"
        "📮 СДЭК:\n"
        "  • Срок: 2–5 дней\n"
        "  • Стоимость: от 200 руб\n\n"
        "После оформления заказа мы свяжемся с вами для уточнения деталей 🤝",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=build_back_markup(),
        parse_mode="Markdown"
    )


# -----------------------
# Помощь
# -----------------------
@bot.callback_query_handler(func=lambda call: call.data == "help")
def help_section(call):

    bot.edit_message_text(
        "❓ *Помощь*\n\n"
        "Если у вас возникли вопросы, мы всегда рады помочь!\n\n"
        "📩 Напишите нам: @your_support_username\n"
        "📞 Телефон: +7 (999) 000-00-00\n"
        "🕐 Режим работы: Пн–Пт с 9:00 до 18:00\n\n"
        "*Частые вопросы:*\n"
        "• Как сделать заказ? — Откройте каталог, выберите товар и нажмите «Купить»\n"
        "• Как отследить заказ? — Свяжитесь с поддержкой, указав номер заказа\n"
        "• Можно ли вернуть товар? — Да, в течение 14 дней при сохранении упаковки",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=build_back_markup(),
        parse_mode="Markdown"
    )


# -----------------------
# Назад в главное меню
# -----------------------
@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main(call):

    bot.edit_message_text(
        "Добро пожаловать в магазин мягких игрушек 🧸\n\n"
        "Выберите раздел:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=build_main_menu_markup(),
    )


# -----------------------
# Запуск
# -----------------------
def main():

    logging.info("🤖 Bot started")

    init_db()
    seed_products()

    catalog.register(bot)
    orders.register(bot)
    admin.register(bot)

    # Работает в цикле, чтобы автоматически восстанавливаться после временных ошибок.
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=30)
        except telebot.apihelper.ApiTelegramException as e:
            logging.error(
                "Ошибка при опросе Telegram API: %s. "
                "Убедитесь, что не запущено несколько экземпляров бота.",
                e,
            )
            time.sleep(5)
        except KeyboardInterrupt:
            logging.info("Остановка бота по сигналу KeyboardInterrupt")
            break
        except Exception:
            logging.exception("Непредвиденная ошибка, перезапуск через 5 секунд")
            time.sleep(5)


if __name__ == "__main__":
    main()
