from flask import Flask

app = Flask(__name__)

from . import views

# Імпорт та реєстрація Blueprint-а users
from .users import user_bp
app.register_blueprint(user_bp)
from .products import products_bp
app.register_blueprint(products_bp)