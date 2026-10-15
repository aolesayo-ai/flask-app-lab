from flask import render_template
from . import products_bp

products = [
    {
        "id": 1,
        "name": "Laptop",
        "price": 1200,
        "content": "Потужний ноутбук з процесором Intel Core i7, 16 ГБ оперативної пам'яті та SSD на 512 ГБ."
    },
    {
        "id": 2,
        "name": "Phone",
        "price": 800,
        "content": "Смартфон із 6.5-дюймовим OLED-дисплеєм, подвійною камерою та акумулятором на 5000 мА·год."
    },
    {
        "id": 3,
        "name": "PC",
        "price": 1800,
        "content": "Настільний комп'ютер для ігор або роботи з графікою: RTX 4070, 32 ГБ RAM, 1 ТБ SSD."
    }
]

@products_bp.route('/products')
def products_list():
    return render_template('products/products.html', products=products)

@products_bp.route('/products/<int:id>')
def detail_product(id):
    # Шукаємо товар за id
    product = next((p for p in products if p['id'] == id), None)
    
    if product:
        return render_template('products/detail_product.html', product=product)
    else:
        return "Товар не знайдено", 404