from flask import (Blueprint, flash, make_response, redirect, render_template, request, session,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user

from app import db

from .forms import LoginForm, RegistrationForm
from .models import User

# Створюємо блюпринт для користувачів
users_bp = Blueprint('users', __name__, template_folder='templates')


# ---------- Лабораторна 9: реєстрація, вхід, вихід ----------

@users_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:          # уже увійшов — реєстрація не потрібна
        return redirect(url_for('users.account'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data.lower())
        user.set_password(form.password.data)  # у БД потрапляє лише bcrypt-хеш
        db.session.add(user)
        db.session.commit()
        flash(f'Акаунт {user.username} створено! Тепер можна увійти.', 'success')
        return redirect(url_for('users.login'))

    if form.is_submitted():
        flash('Реєстрацію не завершено: виправте помилки у формі.', 'error')
    return render_template('users/register.html', form=form, title='Реєстрація')


@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.account'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.email == form.email.data.lower()))
        if user and user.check_password(form.password.data):   # порівняння хешів
            login_user(user, remember=form.remember.data)        # id користувача -> сесія
            session['username'] = user.username
            flash('Успішний вхід до системи!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/') and not next_page.startswith('//'):
                return redirect(next_page)
            return redirect(url_for('users.account'))
        flash('Невірний email або пароль.', 'error')

    return render_template('users/login.html', form=form, title='Вхід')


@users_bp.route('/logout')
def logout():
    logout_user()
    session.pop('username', None)
    flash('Ви вийшли з системи.', 'success')
    return redirect(url_for('users.login'))


@users_bp.route('/account')
@login_required
def account():
    return render_template('users/account.html', title='Мій акаунт')


@users_bp.route('/all')
@login_required
def users_list():
    users = db.session.scalars(db.select(User).order_by(User.id)).all()
    return render_template('users/users.html', users=users, title='Користувачі')


# ---------- Лабораторна 4: кукі та тема (доступно лише після входу) ----------

@users_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')
        resp = make_response(redirect(url_for('users.profile')))

        if action == 'add_cookie':
            key = request.form.get('cookie_key')
            value = request.form.get('cookie_value')
            max_age = request.form.get('cookie_max_age', type=int)
            if key and value:
                resp.set_cookie(key, value, max_age=max_age if max_age else None)
                flash(f'Кукі "{key}" успішно додано!', 'success')
            else:
                flash('Введіть ключ та значення кукі.', 'error')

        elif action == 'delete_cookie':
            key = request.form.get('delete_key')
            if key in request.cookies:
                resp.delete_cookie(key)
                flash(f'Кукі "{key}" успішно видалено!', 'success')
            else:
                flash('Такий ключ кукі не знайдено.', 'error')

        elif action == 'delete_all_cookies':
            for cookie_name in request.cookies:
                resp.delete_cookie(cookie_name)
            flash('Усі кукі успішно видалено!', 'success')

        return resp

    return render_template('users/profile.html', username=current_user.username,
                           cookies=request.cookies)


@users_bp.route('/set-theme/<theme_name>')
def set_theme(theme_name):
    resp = make_response(redirect(url_for('users.profile')))
    if theme_name in ['light', 'dark']:
        resp.set_cookie('theme', theme_name, max_age=60 * 60 * 24 * 30)
        flash(f'Колірну схему змінено на {theme_name}', 'success')
    return resp


# Маршрути з лабораторної №3
@users_bp.route("/hi/<string:name>")
def greetings(name):
    name = name.upper()
    age = request.args.get("age", None, int)
    return render_template("users/hi.html", name=name, age=age)


@users_bp.route("/admin")
def admin():
    to_url = url_for("users.greetings", name="administrator", age=45, _external=True)
    return redirect(to_url)
