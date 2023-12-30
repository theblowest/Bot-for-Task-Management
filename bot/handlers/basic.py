import sys
from telebot import types
from bot.models import User, Session as db_session
from bot.config import TOKEN
from telebot import TeleBot

bot = TeleBot(TOKEN)

# @bot.message_handler(commands=['start'])
# def start(message):
#     # Обработка команды /start
#     user_id = message.from_user.id
#     user_name = message.from_user.username
#     session = db_session()
#     user = session.query(User).filter_by(username=user_id).first()
#     if not user:
#         user = User(username=user_id)
#         session.add(user)
#         session.commit()
#
#     # Отправка приветственного сообщения
#     welcome_message = f"Привет, {user_name}!"
#     bot.send_message(user_id, welcome_message)

@bot.message_handler(commands=['info'])
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

    file = open('../static/inform', 'r', encoding='utf-8')
    txt = file.read()

    bot.send_message(message.chat.id, txt, reply_markup=markup)

@bot.message_handler(commands=['stop'])
def stop(message):
    bot.send_message(message.chat.id, "Бот завершил работу.")
    sys.exit() | bot.stop_bot()
