import os

from flask import Flask, flash, redirect, render_template, request
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from .config import config


class Base(DeclarativeBase):
    """Базовий клас моделей у стилі SQLAlchemy 2.0 з єдиним стилем назв обмежень."""
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
bcrypt = Bcrypt()

# Лабораторна 9: Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'users.login'           # куди перенаправляти неавторизованих
login_manager.login_message = 'Увійдіть, щоб переглянути цю сторінку.'
login_manager.login_message_category = 'info'


def create_app(config_name=None):
    """Application factory: створює застосунок для середовища config_name."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    os.makedirs(app.instance_path, exist_ok=True)

    # розширення
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # маршрути та блюпринти
    from .views import register_routes
    register_routes(app)

    from .users import models as _user_models  # noqa: F401 (щоб Alembic бачив модель)
    from .users.views import users_bp
    app.register_blueprint(users_bp, url_prefix='/users')

    from .products import products_bp
    from .products.storage import init_storage
    app.register_blueprint(products_bp)
    init_storage(app)

    from .posts import post_bp
    app.register_blueprint(post_bp)

    # обробники помилок
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html', title='Сторінку не знайдено'), 404

    @app.errorhandler(413)
    def file_too_large(error):
        flash('Файл занадто великий (максимум 5 МБ на запит).', 'error')
        return redirect(request.url)

    return app
