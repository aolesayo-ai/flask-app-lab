from flask import Blueprint

# Створюємо Blueprint
user_bp = Blueprint('users', __name__, template_folder='templates')

# Імпортуємо маршрути з цього ж модуля
from . import views