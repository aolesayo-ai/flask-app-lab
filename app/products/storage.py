"""Сховище товарів на базі TinyDB (JSON-файл data/products.json)."""
import os
import uuid
from datetime import datetime

from flask import current_app, g
from tinydb import TinyDB

TABLE_NAME = 'products'

# Товари з попередніх лаб — додаються лише при першому створенні файлу БД
SEED_PRODUCTS = [
    {'name': 'Laptop', 'price': 1200.0, 'category': 'electronics', 'quantity': 5, 'image': None,
     'content': "Потужний ноутбук з процесором Intel Core i7, 16 ГБ оперативної пам'яті та SSD на 512 ГБ."},
    {'name': 'Phone', 'price': 800.0, 'category': 'electronics', 'quantity': 10, 'image': None,
     'content': 'Смартфон із 6.5-дюймовим OLED-дисплеєм, подвійною камерою та акумулятором на 5000 мА·год.'},
    {'name': 'PC', 'price': 1800.0, 'category': 'electronics', 'quantity': 3, 'image': None,
     'content': "Настільний комп'ютер для ігор або роботи з графікою: RTX 4070, 32 ГБ RAM, 1 ТБ SSD."},
]


# ---------- TinyDB ----------

def get_db():
    """Одне підключення до TinyDB на запит (зберігається у flask.g)."""
    if 'products_db' not in g:
        g.products_db = TinyDB(
            current_app.config['PRODUCTS_DB'],
            create_dirs=True,
            encoding='utf-8',
            ensure_ascii=False,
            indent=2,
        )
    return g.products_db


def close_db(exc=None):
    db = g.pop('products_db', None)
    if db is not None:
        db.close()


def init_storage(app):
    """Створює JSON-файл і таблицю products, реєструє закриття БД після запиту."""
    app.teardown_appcontext(close_db)
    with app.app_context():
        is_new = not os.path.exists(app.config['PRODUCTS_DB'])
        db = get_db()
        if is_new:
            for product in SEED_PRODUCTS:
                create_product(product)
        elif TABLE_NAME not in db.tables():
            table = db.table(TABLE_NAME)
            table.remove(doc_ids=[table.insert({})])  # створює порожню таблицю у файлі


def _table():
    return get_db().table(TABLE_NAME)


def _to_dict(doc):
    if doc is None:
        return None
    data = dict(doc)
    data['id'] = doc.doc_id
    return data


# ---------- CRUD ----------

def all_products():
    return sorted((_to_dict(d) for d in _table().all()), key=lambda p: p['id'])


def get_product(product_id):
    return _to_dict(_table().get(doc_id=product_id))


def create_product(data):
    record = dict(data)
    record.pop('id', None)
    record['created_at'] = datetime.now().isoformat(sep=' ', timespec='seconds')
    table = _table()
    product_id = table.insert(record)
    table.update({'id': product_id}, doc_ids=[product_id])
    return product_id


def update_product(product_id, data):
    if not _table().contains(doc_id=product_id):
        return False
    changes = {k: v for k, v in data.items() if k not in ('id', 'created_at')}
    _table().update(changes, doc_ids=[product_id])
    return True


def delete_product(product_id):
    if not _table().contains(doc_id=product_id):
        return False
    _table().remove(doc_ids=[product_id])
    return True


# ---------- Зображення ----------

def upload_folder():
    folder = current_app.config.get('PRODUCT_UPLOAD_FOLDER')
    if not folder:
        from . import products_bp
        folder = os.path.join(products_bp.static_folder, 'uploads')
    return folder


def save_image(file_storage):
    """Зберігає файл під UUID-ім'ям, повертає відносний шлях 'uploads/<uuid>.<ext>'."""
    ext = file_storage.filename.rsplit('.', 1)[-1].lower()
    filename = f'{uuid.uuid4().hex}.{ext}'
    folder = upload_folder()
    os.makedirs(folder, exist_ok=True)
    file_storage.save(os.path.join(folder, filename))
    return f'uploads/{filename}'


def image_path(relative_path):
    if not relative_path:
        return None
    return os.path.join(upload_folder(), os.path.basename(relative_path))


def image_exists(relative_path):
    path = image_path(relative_path)
    return bool(path and os.path.isfile(path))


def delete_image(relative_path):
    path = image_path(relative_path)
    if path and os.path.isfile(path):
        os.remove(path)
