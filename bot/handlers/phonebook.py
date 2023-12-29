from bot.handlers.basic import bot
from telebot import types

from bot.models import User, Contact, Session as db_session

@bot.message_handler(commands=['phone_book'])
def phone_book(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    list_of_cont = types.InlineKeyboardButton(
        'Ваша телефонная книга', callback_data='list', switch_inline_query=True,
    )
    add_cont = types.InlineKeyboardButton(
        'Добавить контакт', callback_data='add', switch_inline_query=True
    )
    delete = types.InlineKeyboardButton(
        'Удалить контакт', callback_data='delete', switch_inline_query=True
    )
    markup.add(list_of_cont, add_cont, delete)

    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data == 'list':
        list(call.message)
    elif call.data == 'add':
        add(call.message)
    elif call.data == 'delete':
        delete(call.message)

@bot.message_handler(commands=['add'])
def add(message):
    bot.send_message(message.chat.id, "Введите имя контакта:")
    bot.register_next_step_handler(message, add_contact)


def add_contact(message):
    name = message.text
    user_id = message.from_user.id
    session = db_session()

    user = session.query(User).filter_by(username=user_id).first()
    contact = Contact(name=name, user=user)
    session.add(contact)
    session.commit()

    bot.send_message(message.chat.id, f"Контакт {name} добавлен!")


@bot.message_handler(commands=['list'])
def list(message):
    user_id = message.from_user.id
    session = db_session()

    user = session.query(User).filter_by(username=user_id).first()
    if not user or not user.phonebook:
        bot.send_message(message.chat.id, "У вас нет контактов.")
        return

    contacts = "\n".join([f"{contact.name}: {contact.phone_number}" for contact in user.phonebook])
    bot.send_message(message.chat.id, f"Ваши контакты:\n{contacts}")


@bot.message_handler(commands=['delete'])
def delete(message):
    bot.send_message(message.chat.id, "Введите имя контакта для удаления:")
    bot.register_next_step_handler(message, delete_contact)


def delete_contact(message):
    name = message.text
    user_id = message.from_user.id
    session = db_session()

    user = session.query(User).filter_by(username=user_id).first()
    contact = session.query(Contact).filter_by(name=name, user=user).first()

    if contact:
        session.delete(contact)
        session.commit()
        bot.send_message(message.chat.id, f"Контакт {name} удален!")
    else:
        bot.send_message(message.chat.id, f"Контакт {name} не найден.")