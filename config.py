import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'clothbook-super-secret-key-2026')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'clothbook-jwt-key-2026')
    
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
    MYSQL_DB = os.getenv('MYSQL_DB', 'clothbook_db')

    # Fallback to SQLite if MySQL is not available locally for rapid preview
    USE_SQLITE = os.getenv('USE_SQLITE', 'false').lower() == 'true'

    if USE_SQLITE:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///clothbook.db'
    else:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
