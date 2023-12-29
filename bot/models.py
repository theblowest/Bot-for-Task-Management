from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(Integer, unique=True, nullable=False)

    phonebook_id = Column(Integer, ForeignKey('contacts.id'))
    phonebook = relationship("contacts", back_populates="user")

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    username = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    phone_number = Column(String)
    user = relationship('User', back_populates='phonebook')


engine = create_engine('sqlite:///bot.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
