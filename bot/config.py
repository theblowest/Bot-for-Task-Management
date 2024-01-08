from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.environ.get("TOKEN")
DEBUG = os.environ.get("DEBUG")
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")