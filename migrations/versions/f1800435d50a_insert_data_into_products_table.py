"""Insert data into products table

Revision ID: f1800435d50a
Revises: 8d94d31d367f
Create Date: 2026-11-19 12:14:23.439318

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1800435d50a'
down_revision = '8d94d31d367f'
branch_labels = None
depends_on = None


CATEGORIES = ['Smartphones', 'Tablets', 'Accessories']

PRODUCTS = [
    # (назва, ціна, категорія)
    ('Samsung Galaxy S24', 899.99, 'Smartphones'),
    ('Google Pixel 8', 699.00, 'Smartphones'),
    ('iPad Air', 599.00, 'Tablets'),
    ('Samsung Galaxy Tab S9', 799.00, 'Tablets'),
    ('MacBook Air M3', 1299.00, 'Laptops'),
    ('Lenovo ThinkPad X1', 1450.00, 'Laptops'),
    ('AirPods Pro', 249.00, 'Accessories'),
    ('Logitech MX Master 3S', 99.99, 'Accessories'),
]


def upgrade():
    # 1. Категорії: ON CONFLICT (name) DO NOTHING не дублює вже наявні (наприклад, Laptops)
    for name in CATEGORIES + ['Laptops']:
        op.execute(
            sa.text('INSERT INTO categories (name) VALUES (:name) '
                    'ON CONFLICT (name) DO NOTHING').bindparams(name=name)
        )

    # 2. Товари: id категорії знаходимо підзапитом за її назвою
    for name, price, category in PRODUCTS:
        op.execute(
            sa.text('INSERT INTO products (name, price, active, category_id) '
                    'VALUES (:name, :price, 1, '
                    '(SELECT id FROM categories WHERE name = :category))')
            .bindparams(name=name, price=price, category=category)
        )


def downgrade():
    # Відкат: видаляємо лише ті записи, які додала ця міграція
    for name, _, _ in PRODUCTS:
        op.execute(sa.text('DELETE FROM products WHERE name = :name').bindparams(name=name))
    for name in CATEGORIES:
        op.execute(sa.text('DELETE FROM categories WHERE name = :name').bindparams(name=name))
