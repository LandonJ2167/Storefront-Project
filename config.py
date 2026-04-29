import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-this"
    SQLALCHEMY_DATABASE_URI = "sqlite:///bytesupply.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False