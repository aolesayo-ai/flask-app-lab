import os

from flask import Flask

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key_123'  # Обов'язково для роботи сесій і CSRF!

# Лабораторна №5
app.config['CONTACT_LOG'] = os.path.join(BASE_DIR, 'logs', 'contact.log')

from . import views

from .users.views import users_bp
app.register_blueprint(users_bp, url_prefix='/users')

from .products import products_bp
app.register_blueprint(products_bp)
