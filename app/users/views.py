from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response

# Створюємо блюпринт для користувачів
users_bp = Blueprint('users', __name__, template_folder='templates')

USERS_STUB = {
    "user1": "password123",
    "admin": "admin"
}

@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS_STUB and USERS_STUB[username] == password:
            session['username'] = username
            flash('Успішний вхід до системи!', 'success')
            return redirect(url_for('users.profile'))
        else:
            flash('Wrong data! Try again!', 'error')
            return redirect(url_for('users.login'))
            
    return render_template('users/login.html')

@users_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        flash('Будь ласка, увійдіть у систему спочатку.', 'error')
        return redirect(url_for('users.login'))
    
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

    username = session['username']
    cookies_dict = request.cookies
    return render_template('users/profile.html', username=username, cookies=cookies_dict)

@users_bp.route('/logout')
def logout():
    session.pop('username', None)
    flash('Ви вийшли з системи.', 'success')
    return redirect(url_for('users.login'))

@users_bp.route('/set-theme/<theme_name>')
def set_theme(theme_name):
    resp = make_response(redirect(url_for('users.profile')))
    if theme_name in ['light', 'dark']:
        resp.set_cookie('theme', theme_name, max_age=60*60*24*30)
        flash(f'Колірну схему змінено на {theme_name}', 'success')
    return resp