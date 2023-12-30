import telebot
from sqlalchemy.orm import sessionmaker

from bot.config import TOKEN
from bot.handlers import info
from models import User, Contact, engine

# Підключення до бази даних
Session = sessionmaker(bind=engine)
session = Session()

# Ініціалізація бота
bot = telebot.TeleBot(TOKEN)

# Команда /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Перевірка, чи користувач вже зареєстрований
    user = session.query(User).filter_by(chat_id=message.chat.id).first()
    if not user:
        bot.send_message(message.chat.id, "Вас не зареєстровано. Будь ласка, введіть логін та пароль.")
    else:
        bot.send_message(message.chat.id, f"Привіт, {user.username}!")
        bot.register_next_step_handler(message, next_handler)


# Обробник введення логіну та паролю
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

def next_handler(message):
    if message.text == 'info':
        info(message)
    else:
        bot.send_message(message.chat.id, "Невідома команда. Спробуйте ще раз.")

if __name__ == "__main__":
    bot.polling(none_stop=True)