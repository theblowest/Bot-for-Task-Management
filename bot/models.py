from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from bot.config import SQLALCHEMY_DATABASE_URI

Base = declarative_base()

# Модель користувача
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    username = Column(String)

    contacts = relationship('Contact', secondary='user_contact')
    events = relationship('Event', secondary='user_events', back_populates='user')


# Модель контакту
class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone_number = Column(String)

# Таблиця для зв'язку багато-до-багатьох
    user_contact = Table('user_contact', Base.metadata,
                         Column('user_id', ForeignKey('users.id'), primary_key=True),
                         Column('contact_id', ForeignKey('contacts.id'), primary_key=True))


# Модель події (напоминання)
class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    event_time = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='events')


# Таблиця для зв'язку багато-до-багатьох для подій
    user_events = Table('user_events', Base.metadata,
                        Column('user_id', ForeignKey('users.id'), primary_key=True),
                        Column('event_id', ForeignKey('events.id'), primary_key=True))


engine = create_engine(SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)