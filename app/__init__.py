import os

from flask import Flask, flash, redirect, request

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key_123'  # Обов'язково для роботи сесій і CSRF!

# Лабораторна №5
app.config['CONTACT_LOG'] = os.path.join(BASE_DIR, 'logs', 'contact.log')
app.config['PRODUCTS_DB'] = os.path.join(BASE_DIR, 'data', 'products.json')
app.config['PRODUCT_UPLOAD_FOLDER'] = None          # None -> app/products/static/uploads
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 МБ на запит (на файл — 2 МБ у формі)

from . import views

from .users.views import users_bp
app.register_blueprint(users_bp, url_prefix='/users')

from .products import products_bp
from .products.storage import init_storage
app.register_blueprint(products_bp)
init_storage(app)


@app.errorhandler(413)
def file_too_large(error):
    flash('Файл занадто великий (максимум 5 МБ на запит).', 'error')
    return redirect(request.url)
