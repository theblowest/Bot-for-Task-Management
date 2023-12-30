from datetime import datetime
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.handlers.basic import bot

from bot.main import session
from bot.models import User, Event

last_update = None

# Команда /phonebook
@bot.message_handler(commands=['events'])
def events(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        markup = types.InlineKeyboardMarkup(row_width=1)
        create_event = types.InlineKeyboardButton(
            'Створити нагадування', callback_data='create', switch_inline_query=True,
        )
        check_events = types.InlineKeyboardButton(
            'Переглянути дійсні нагадування', callback_data='check', switch_inline_query=True
        )
        change_event = types.InlineKeyboardButton(
            'Змінити нагадуваняя', callback_data='change_event', switch_inline_query=True
        )
        delete_event = types.InlineKeyboardButton(
            'Видалити нагадування', callback_data='delete_event', switch_inline_query=True
        )

        markup.add(create_event, check_events, change_event, delete_event)
        bot.send_message(chat_id, "Ви увійшли в телефонну книгу.", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")

# Команда /create_event
@bot.message_handler(commands=['create_event'])
def create_event(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        bot.send_message(chat_id, "Введіть назву події:")
        bot.register_next_step_handler(message, enter_event_title, user)
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")


def enter_event_title(message, user):
    chat_id = message.chat.id
    event_title = message.text
    bot.send_message(chat_id, "Введіть опис події:")
    bot.register_next_step_handler(message, enter_event_description, user, event_title)


def enter_event_description(message, user, event_title):
    chat_id = message.chat.id
    event_description = message.text
    bot.send_message(chat_id, "Введіть час події у форматі %DD:%MM:%YYYY %HH:%MM:")
    bot.register_next_step_handler(message, enter_event_time, user, event_title, event_description)


def enter_event_time(message, user, event_title, event_description):
    chat_id = message.chat.id
    event_time_str = message.text

    try:
        event_time = datetime.strptime(event_time_str, '%d:%m:%Y %H:%M')
        new_event = Event(title=event_title, description=event_description, event_time=event_time, user=user)
        session.add(new_event)
        session.commit()

        bot.send_message(chat_id, f"Подія {event_title} створена на {event_time}.")

    except ValueError:
        bot.send_message(chat_id, "Неправильний формат часу. Спробуйте ще раз.")


# Команда /check_events
@bot.message_handler(commands=['check_events'])
def check_events(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        events = user.events
        if events:
            event_list = "\n".join([f"{event.title} ({event.event_time})" for event in events])
            bot.send_message(chat_id, f"Ваші події:\n{event_list}")
        else:
            bot.send_message(chat_id, "У вас немає подій.")
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")


# Команда /change_event
def change_event(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        events = user.events
        if events:
            keyboard = InlineKeyboardMarkup()
            for event in events:
                button = InlineKeyboardButton(text=event.title, callback_data=f'change_{event.id}')
                keyboard.add(button)

            bot.send_message(chat_id, "Виберіть подію для зміни:", reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "У вас немає подій.")
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")

# Обробник Inline-кнопок для зміни події
@bot.callback_query_handler(func=lambda call: call.data.startswith('change'))
def change_event_callback(call):
    chat_id = call.message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        event_id = int(call.data.split('_')[1])
        event = session.query(Event).get(event_id)

        if event in user.events:
            bot.send_message(chat_id, f"Вибрана подія: {event.title}\n"
                                      f"Поточний час події: {event.event_time}\n"
                                      "Введіть новий час події у форматі %d:%m:%Y %H:%M:")
            bot.register_next_step_handler(call.message, change_event_time, user, event)
        else:
            bot.send_message(chat_id, "Ця подія не належить вам.")
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")

def change_event_time(message, user, event):
    chat_id = message.chat.id
    new_event_time_str = message.text

    try:
        new_event_time = datetime.strptime(new_event_time_str, '%d:%m:%Y %H:%M')
        event.event_time = new_event_time
        session.commit()

        bot.send_message(chat_id, f"Час події {event.title} змінено на {new_event_time}.")

    except ValueError:
        bot.send_message(chat_id, "Неправильний формат часу. Спробуйте ще раз.")


# Команда /delete_event
@bot.message_handler(commands=['delete_event'])
def delete_event(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        events = user.events
        if events:
            keyboard = InlineKeyboardMarkup()
            for event in events:
                button = InlineKeyboardButton(text=event.title, callback_data=f'delete_{event.id}')
                keyboard.add(button)

            bot.send_message(chat_id, "Виберіть подію для видалення:", reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "У вас немає подій.")
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")


# Обробник Inline-кнопок для видалення події
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete'))
def delete_event_callback(call):
    chat_id = call.message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        event_id = int(call.data.split('_')[1])
        event = session.query(Event).get(event_id)

        if event in user.events:
            session.delete(event)
            session.commit()
            bot.send_message(chat_id, f"Подію {event.title} видалено.")
        else:
            bot.send_message(chat_id, "Ця подія не належить вам.")
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")
