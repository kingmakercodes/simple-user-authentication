from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import DevelopmentConfig
from argon2 import PasswordHasher
from flask_mail import Mail

# define instances
database= SQLAlchemy()
mail= Mail()
password_hasher= PasswordHasher()

# create application
def create_app():
    app= Flask(__name__)

    # app configurations (to be loaded from app/config.py)
    app.config.from_object(DevelopmentConfig)

    # initialise global application instances
    database.init_app(app)
    mail.init_app(app)

    # register all route blueprint
    from app.routes.auth.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    # create necessary databases
    with app.app_context():
        # import models here
        database.create_all()

    return app