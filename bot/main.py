import telebot
from bot import log
from handlers import basic, bot
from handlers import phonebook
from config import TOKEN

def main():
    bot.add_message_handler(basic.start)
    bot.add_message_handler(phonebook.phone_book)


if __name__ == "__main__":
    bot.polling(none_stop=True)