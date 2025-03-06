import os

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"  # Change for PostgreSQL/MySQL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)  # Used for session security
