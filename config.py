# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///books.db'  # For demo, using SQLite; replace with your DB URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
