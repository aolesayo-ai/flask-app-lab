from decimal import Decimal

from flask import flash, redirect, render_template, url_for
from werkzeug.datastructures import FileStorage

from . import products_bp
from . import storage
from .forms import CATEGORY_LABELS, DeleteForm, ProductForm


@products_bp.app_template_global()
def product_image_url(product):
    """URL зображення або None, якщо зображення немає чи файл відсутній."""
    image = product.get('image') if product else None
    if image and storage.image_exists(image):
        return url_for('products.static', filename=image)
    return None


@products_bp.app_template_filter('category_label')
def category_label(value):
    return CATEGORY_LABELS.get(value, value or '—')


def _has_new_file(field):
    return isinstance(field.data, FileStorage) and bool(field.data.filename)


def _form_to_record(form):
    return {
        'name': form.name.data.strip(),
        'content': form.content.data.strip(),
        'price': float(round(form.price.data, 2)),
        'category': form.category.data,
        'quantity': form.quantity.data,
    }


def _not_found(product_id):
    return render_template('products/not_found.html', product_id=product_id), 404


# ---------- Read ----------

@products_bp.route('')
def products_list():
    return render_template('products/products.html',
                           products=storage.all_products(), delete_form=DeleteForm())


@products_bp.route('/<int:id>')
def detail_product(id):
    product = storage.get_product(id)
    if product is None:
        return _not_found(id)
    return render_template('products/detail_product.html', product=product, delete_form=DeleteForm())


# ---------- Create ----------

@products_bp.route('/add', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        record = _form_to_record(form)
        record['image'] = storage.save_image(form.image.data) if _has_new_file(form.image) else None
        product_id = storage.create_product(record)
        flash(f"Товар «{record['name']}» додано.", 'success')
        return redirect(url_for('products.detail_product', id=product_id))  # PRG

    if form.is_submitted():
        flash('Товар не збережено: виправте помилки у формі.', 'error')
    return render_template('products/product_form.html', form=form, title='Новий товар', product=None)


# ---------- Update ----------

@products_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_product(id):
    product = storage.get_product(id)
    if product is None:
        return _not_found(id)

    initial = {k: v for k, v in product.items() if k != 'image'}
    initial['price'] = Decimal(str(product['price']))
    form = ProductForm(data=initial)

    if form.validate_on_submit():
        changes = _form_to_record(form)
        if _has_new_file(form.image):  # новий файл замінює старий, інакше залишаємо попередній
            changes['image'] = storage.save_image(form.image.data)
            storage.delete_image(product.get('image'))
        storage.update_product(id, changes)
        flash(f"Товар «{changes['name']}» оновлено.", 'success')
        return redirect(url_for('products.detail_product', id=id))

    if form.is_submitted():
        flash('Зміни не збережено: виправте помилки у формі.', 'error')
    return render_template('products/product_form.html', form=form, title='Редагування товару', product=product)


# ---------- Delete ----------

@products_bp.route('/<int:id>/delete', methods=['POST'])
def delete_product(id):
    form = DeleteForm()
    if not form.validate_on_submit():
        flash('Недійсний запит на видалення (CSRF).', 'error')
        return redirect(url_for('products.products_list'))

    product = storage.get_product(id)
    if product is None:
        flash(f'Товар #{id} не знайдено.', 'warning')
        return redirect(url_for('products.products_list'))

    storage.delete_product(id)
    storage.delete_image(product.get('image'))
    flash(f"Товар «{product['name']}» видалено.", 'success')
    return redirect(url_for('products.products_list'))
