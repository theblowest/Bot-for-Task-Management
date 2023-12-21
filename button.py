import sys

import telebot
from telebot import types

bot = telebot.TeleBot('6810282272:AAFUIAzV9cYREh9IkC1ZjfhoEjDtwT2Wdmo')

@bot.message_handler(commands=['start'])
def start(message):
    # Обработка команды /start
    user_id = message.from_user.id
    user_name = message.from_user.username

    # Отправка приветственного сообщения
    welcome_message = f"Привет, {user_name}! Бот успешно запущен."
    bot.send_message(user_id, welcome_message)


@bot.message_handler(commands=['inform'])
def info(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    phone_book = types.InlineKeyboardButton(
        'Ваша телефонная книга', callback_data='phone_book', switch_inline_query=True
    )
    add_reminder = types.InlineKeyboardButton(
        'Добавить напоминание', callback_data='add_reminder', switch_inline_query=True
    )
    check_active_rem = types.InlineKeyboardButton(
        'Посмотреть активные напоминания', callback_data='check_active_rem', switch_inline_query=True
    )
    markup.add(phone_book, add_reminder, check_active_rem)

    file = open('inform', 'r', encoding='utf-8')
    txt = file.read()

    bot.send_message(message.chat.id, txt, reply_markup=markup)

@bot.message_handler(commands=['stop'])
def stop(message):
    bot.send_message(message.chat.id, "Бот завершает выполнение.")
    sys.exit() | bot.stop_bot()


if __name__ == "__main__":
    bot.polling(none_stop=True)