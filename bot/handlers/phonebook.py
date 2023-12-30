from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.handlers.basic import bot
from telebot import types

from bot.main import session
from bot.models import User, Contact


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
        markup.add(list_contacts, add_contact, delete_contact)
        bot.send_message(chat_id, "Ви увійшли в телефонну книгу.", reply_markup=markup)
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


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'list':
        list_contacts(call.message)
    elif call.data == 'add':
        add_contact(call.message)
    elif call.data == 'delete':
        delete_contact(call.message)