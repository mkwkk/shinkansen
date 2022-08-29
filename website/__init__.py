from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from .langconfig import switch_language

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['LANGUAGES'] = ['ja', 'vi', 'en']
    app.config['SECRET_KEY'] = "helloworld"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = "false"
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .home import homepage

    app.register_blueprint(views)
    app.register_blueprint(auth)
    app.register_blueprint(homepage)

    from .models import User, Post, Comment, Like

    create_database(app)
    switch_language()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists("website/" + DB_NAME):
        db.create_all(app=app)
        print("Created database!")
