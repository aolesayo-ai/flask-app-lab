import logging
import os

from flask import current_app, flash, redirect, render_template, url_for

from . import app
from .forms import ContactForm


def get_contact_logger():
    """Логер, що дописує дані контактної форми у файл CONTACT_LOG."""
    path = os.path.abspath(current_app.config['CONTACT_LOG'])
    logger = logging.getLogger('contact')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    # якщо шлях до логу змінився (наприклад, у тестах) — перевідкриваємо файл
    for handler in list(logger.handlers):
        if getattr(handler, 'baseFilename', None) != path:
            logger.removeHandler(handler)
            handler.close()
    if not logger.handlers:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        handler = logging.FileHandler(path, encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
        logger.addHandler(handler)
    return logger


@app.route('/')
@app.route('/resume')
def resume():
    return render_template('resume.html', title='Моє Резюме')


@app.route('/contacts', methods=['GET', 'POST'])  # стара адреса з лаб 2–4
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        try:
            get_contact_logger().info(
                'name=%s | email=%s | phone=%s | subject=%s | message=%s',
                form.name.data,
                form.email.data,
                form.phone.data,
                form.subject.data,
                form.message.data.replace('\n', ' '),
            )
        except OSError:
            current_app.logger.exception('Не вдалося записати контактний лог')
            flash('Не вдалося зберегти повідомлення. Спробуйте пізніше.', 'error')
            return redirect(url_for('contact'))

        flash(f'Дякуємо, {form.name.data}! Ваше повідомлення надіслано.', 'success')
        return redirect(url_for('contact'))  # Post/Redirect/Get

    if form.is_submitted():
        flash('Повідомлення не надіслано: виправте помилки у формі.', 'error')

    return render_template('contacts.html', title='Контакти', form=form)
