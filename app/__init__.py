from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key_123'  # Обов'язково для роботи сесій!

from . import views

from .users.views import users_bp
app.register_blueprint(users_bp, url_prefix='/users')

from .products import products_bp
app.register_blueprint(products_bp)