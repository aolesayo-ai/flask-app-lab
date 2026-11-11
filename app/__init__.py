import os

from flask import Flask, flash, redirect, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from .config import config


class Base(DeclarativeBase):
    """Базовий клас моделей у стилі SQLAlchemy 2.0."""


db = SQLAlchemy(model_class=Base)
migrate = Migrate()


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

    # маршрути та блюпринти
    from .views import register_routes
    register_routes(app)

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
