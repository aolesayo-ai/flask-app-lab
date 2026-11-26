import unittest

from app import create_app, db
from app.users.models import User


class AuthTestCase(unittest.TestCase):
    """Лабораторна 9: реєстрація, вхід/вихід, Flask-Login."""

    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    # ---------- helpers ----------

    def register(self, **overrides):
        data = {
            'username': 'olesia',
            'email': 'olesia@example.com',
            'password': 'secret123',
            'confirm_password': 'secret123',
        }
        data.update(overrides)
        return self.client.post('/users/register', data=data)

    def login(self, email='olesia@example.com', password='secret123', **kwargs):
        return self.client.post('/users/login', data={'email': email, 'password': password},
                                **kwargs)

    def create_user(self, username='olesia', email='olesia@example.com', password='secret123'):
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def text(self, response):
        return response.get_data(as_text=True)

    # ---------- Views: сторінки завантажуються ----------

    def test_register_page_loads(self):
        response = self.client.get('/users/register')
        self.assertEqual(response.status_code, 200)
        html = self.text(response)
        for field in ('username', 'email', 'password', 'confirm_password'):
            self.assertIn(f'name="{field}"', html)

    def test_login_page_loads(self):
        response = self.client.get('/users/login')
        self.assertEqual(response.status_code, 200)
        html = self.text(response)
        for field in ('email', 'password', 'remember'):
            self.assertIn(f'name="{field}"', html)

    # ---------- Реєстрація ----------

    def test_register_saves_user_with_hashed_password(self):
        response = self.register()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/users/login'))

        user = db.session.scalar(db.select(User).where(User.username == 'olesia'))
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'olesia@example.com')
        self.assertNotEqual(user.password, 'secret123')       # відкритий пароль не зберігається
        self.assertTrue(user.password.startswith('$2b$'))     # bcrypt-хеш
        self.assertTrue(user.check_password('secret123'))
        self.assertFalse(user.check_password('wrong'))

    def test_register_duplicate_username_and_email(self):
        self.create_user()
        response = self.register()
        self.assertEqual(response.status_code, 200)
        html = self.text(response)
        self.assertIn('Користувач із таким іменем вже існує', html)
        self.assertIn('Цей email вже зареєстровано', html)
        self.assertEqual(len(db.session.scalars(db.select(User)).all()), 1)

    def test_register_validation_errors(self):
        response = self.register(username='1ab', email='not-an-email',
                                 password='123', confirm_password='321')
        html = self.text(response)
        self.assertIn('від 4 до 14 символів', html)
        self.assertIn('коректну email-адресу', html)
        self.assertIn('не коротшим за 6 символів', html)
        self.assertIn('Паролі не збігаються', html)
        self.assertEqual(db.session.scalars(db.select(User)).all(), [])

    # ---------- Вхід і вихід ----------

    def test_login_success_redirects_to_account(self):
        self.create_user()
        response = self.login()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/users/account'))

        html = self.text(self.client.get('/users/account'))
        self.assertIn('olesia@example.com', html)
        self.assertIn('Вихід', html)              # меню для авторизованого
        self.assertNotIn('Реєстрація</a>', html)

    def test_login_wrong_password(self):
        self.create_user()
        response = self.login(password='wrong-password')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Невірний email або пароль', self.text(response))
        self.assertEqual(self.client.get('/users/account').status_code, 302)  # не увійшли

    def test_logout(self):
        self.create_user()
        self.login()
        response = self.client.get('/users/logout', follow_redirects=True)
        self.assertIn('Ви вийшли з системи', self.text(response))
        response = self.client.get('/users/account')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login', response.location)

    # ---------- @login_required ----------

    def test_protected_pages_redirect_anonymous_to_login(self):
        for url in ('/users/account', '/users/all', '/users/profile'):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn('/users/login?next=', response.location)

    def test_users_list_shows_all_users_and_count(self):
        self.create_user()
        self.create_user('andrii', 'andrii@example.com')
        self.login()
        html = self.text(self.client.get('/users/all'))
        self.assertIn('Усього: 2', html)
        self.assertIn('andrii@example.com', html)

    def test_authenticated_user_is_redirected_from_register(self):
        self.create_user()
        self.login()
        response = self.client.get('/users/register')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/users/account'))


if __name__ == '__main__':
    unittest.main()
