import os
from dotenv import load_dotenv

load_dotenv()

# application configuration
class Config:
    SECRET_KEY= os.getenv('SECRET_KEY')

    # SQLALCHEMY configuration
    SQLALCHEMY_DATABASE_URI= os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/my_flask_app')
    SQLALCHEMY_TRACK_MODIFICATIONS= False

    # JWT configuration
    JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'jwt_secret_key')
    JWT_TOKEN_LOCATION= os.getenv('JWT_TOKEN_LOCATION', 'headers').split(',')
    JWT_HEADER_NAME= os.getenv('JWT_HEADER_NAME', 'Authorization')
    JWT_HEADER_TYPE= os.getenv('JWT_HEADER_TYPE', 'Bearer')

    # FLASK-MAIL configuration keys
    MAIL_SERVER= os.getenv('MAIL_SERVER')
    MAIL_PORT= os.getenv('MAIL_PORT')
    MAIL_USE_TLS= os.getenv('MAIL_USE_TLS')
    MAIL_USE_SSL= os.getenv('MAIL_USE_SSL')
    MAIL_USERNAME= os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD= os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER= os.getenv('MAIL_DEFAULT_SENDER')

class DevelopmentConfig(Config):
    DEBUG= True

class ProductionConfig(Config):
    DEBUG= False