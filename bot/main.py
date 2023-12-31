from datetime import datetime

import telebot
from telebot import types
from sqlalchemy.orm import sessionmaker
import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import TOKEN
from bot.handlers import info
from models import User, Contact, engine, Event

# Підключення до бази даних
Session = sessionmaker(bind=engine)
session = Session()

# Ініціалізація бота
bot = telebot.TeleBot(TOKEN)

# Глобальний контекст для зберігання станів обробника
global_context = {}


# Команда /start
@bot.message_handler(commands=['start', 'menu'])
def handle_start(message):
    print('BOT STARTED')
    # Перевірка, чи користувач вже зареєстрований
    user = session.query(User).filter_by(chat_id=message.chat.id).first()
    chat_id = message.chat.id
    if not user:
        bot.send_message(message.chat.id, "Вас не зареєстровано. Будь ласка, введіть логін.")
    else:
        bot.send_message(message.chat.id, f"Привіт, {user.username}!")
        markup = types.InlineKeyboardMarkup(row_width=1)
        phone_book = types.InlineKeyboardButton(
            'Ваша телефонная книга', callback_data='phone_book', switch_inline_query=True
        )
        add_reminder = types.InlineKeyboardButton(
            'Напоминания', callback_data='reminders', switch_inline_query=True
        )

        markup.add(phone_book, add_reminder)

        file = open('static/menu', 'r', encoding='utf-8')
        txt = file.read()

        bot.send_message(message.chat.id, txt, reply_markup=markup)
        global_context[chat_id] = 'menu'

@bot.callback_query_handler(func=lambda call: call.data in {'phone_book', 'reminders'})
def phonebook_callback(call):
    chat_id = call.message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        # Викликати відповідний обробник в залежності від поточного стану
        if call.data == "phone_book":
            phonebook(call.message)
            global_context[chat_id] = 'phonebook'
        elif call.data == "reminders":
            events(call.message)
            global_context[chat_id] = 'events'
        else:
            bot.send_message(chat_id, "Непередбачений стан. Почніть з команди /phonebook.")
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")


# Команда /phonebook
@bot.message_handler(commands=['phonebook'])
def phonebook(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        markup = types.InlineKeyboardMarkup(row_width=1)
        list_contacts = types.InlineKeyboardButton(
            'Ваша телефонная книга', callback_data='list', switch_inline_query=True,
        )
        add_contact = types.InlineKeyboardButton(
            'Добавить контакт', callback_data='add', switch_inline_query=True
        )
        delete_contact = types.InlineKeyboardButton(
            'Удалить контакт', callback_data='delete', switch_inline_query=True
        )
        menu = types.InlineKeyboardButton(
            'Меню', callback_data='menu', switch_inline_query=True
        )
        markup.add(list_contacts, add_contact, delete_contact, menu)
        bot.send_message(chat_id, "Ви увійшли в телефонну книгу.", reply_markup=markup)
        # Встановлення поточного стану в глобальному контексті
        global_context[chat_id] = "phonebook"
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")


# Команда /add_contact
@bot.message_handler(commands=['add_contact'])
def add_contact(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
            bot.send_message(chat_id, "Введіть ім'я контакту:")
            bot.register_next_step_handler(message, add_contact_name)
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")

def add_contact_name(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        contact_name = message.text
        bot.send_message(chat_id, "Введіть номер телефону контакту:")
        bot.register_next_step_handler(message, add_contact_number, contact_name)
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")

def add_contact_number(message, contact_name):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        contact_number = message.text

        # Створення нового контакту
        new_contact = Contact(name=contact_name, phone_number=contact_number)
        user.contacts.append(new_contact)
        session.commit()

        bot.send_message(chat_id, f"Контакт {contact_name} доданий!")
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")


# Команда /delete_contact
@bot.message_handler(commands=['delete_contact'])
def delete_contact(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        contacts = user.contacts
        if contacts:
            keyboard = InlineKeyboardMarkup()
            for contact in contacts:
                button = InlineKeyboardButton(text=contact.name, callback_data=str(contact.id))
                keyboard.add(button)

            bot.send_message(chat_id, "Виберіть контакт для видалення:", reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "У вас немає контактів.")
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")

# Обробник Inline-кнопок для видалення контакту
@bot.callback_query_handler(func=lambda call: True)
def delete_contact_callback(call):
    chat_id = call.message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        contact_id = int(call.data)
        contact = session.query(Contact).get(contact_id)

        if contact in user.contacts:
            user.contacts.remove(contact)
            session.commit()
            bot.send_message(chat_id, f"Контакт {contact.name} видалено!")
        else:
            bot.send_message(chat_id, "Цей контакт не належить вам.")
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")

# Команда /list_contacts
@bot.message_handler(commands=['list_contacts'])
def list_contacts(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        contacts = user.contacts
        if contacts:
            contact_list = "\n".join([f"{contact.name}: {contact.phone_number}" for contact in contacts])
            bot.send_message(chat_id, f"Ваші контакти:\n{contact_list}")
        else:
            bot.send_message(chat_id, "У вас немає контактів.")
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")

# Обробник для команди /phonebook
@bot.callback_query_handler(func=lambda call: call.data in {'list', 'add', 'delete'})
def phonebook_callback(call):
    chat_id = call.message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        # Викликати відповідний обробник в залежності від поточного стану
        if global_context.get(chat_id) == "phonebook":
            if call.data == 'list':
                list_contacts(call.message)
            elif call.data == 'add':
                add_contact(call.message)
            elif call.data == 'delete':
                delete_contact(call.message)
            elif call.data == 'menu':
                global_context[chat_id] = 'menu'
        else:
            bot.send_message(chat_id, "Непередбачений стан. Почніть з команди /phonebook.")
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")


# Команда /events
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
        menu = types.InlineKeyboardButton(
            'Меню', callback_data='menu', switch_inline_query=True
        )
        markup.add(create_event, check_events, change_event, delete_event)
        bot.send_message(chat_id, "Ви в розділ нагадувань.", reply_markup=markup)
        global_context[chat_id] = 'events'
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

@bot.callback_query_handler(func=lambda call: call.data in {'create', 'check', 'change_event', 'delete_event'})
def events_callback(call):
    chat_id = call.message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        # Викликати відповідний обробник в залежності від поточного стану
        if global_context.get(chat_id) == "events":
            if call.data == 'create':
                create_event(call.message)
            elif call.data == 'check':
                check_events(call.message)
            elif call.data == 'change_event':
                change_event(call.message)
            elif call.data == 'delete_event':
                delete_event(call.message)
            elif call.data == 'menu':
                global_context[chat_id] = 'menu'
        else:
            bot.send_message(chat_id, "Непередбачений стан. Почніть з команди /events.")
    else:
        bot.send_message(chat_id, "Ви не авторизовані. Будь ласка, введіть логін.")

# Обробник введення логіну
@bot.message_handler(func=lambda message: True)
def handle_login(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if not user:
        # Реєстрація нового користувача
        user = User(chat_id=chat_id, username=message.text)
        session.add(user)
        session.commit()
        bot.send_message(chat_id, f"Ви зареєстровані, {user.username}!")
    else:
        # Авторизація
        if message.text == user.username:
            bot.send_message(chat_id, f"Ви авторизовані, {user.username}!")
        else:
            bot.send_message(chat_id, "Неправильний логін. Спробуйте ще раз.")


if __name__ == "__main__":
    bot.polling(none_stop=True)