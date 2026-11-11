import unittest
from datetime import datetime

from app import create_app, db
from app.posts.models import Post


def post_data(**overrides):
    data = {
        'title': 'Перший пост',
        'content': 'Текст першого поста',
        'category': 'news',
        'publish_date': '2026-11-07T12:30',
        'enabled': 'y',
    }
    data.update(overrides)
    return data


class PostCrudTestCase(unittest.TestCase):
    """Модульні тести CRUD-операцій блюпринта posts (Flask-SQLAlchemy)."""

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

    def add(self, **kwargs):
        post = Post(**{'title': 'Пост', 'content': 'Контент', 'category': 'tech', **kwargs})
        db.session.add(post)
        db.session.commit()
        return post

    def text(self, response):
        return response.get_data(as_text=True)

    # ---------- Model ----------

    def test_model_defaults_and_repr(self):
        post = self.add()
        self.assertTrue(post.is_active)
        self.assertEqual(post.author, 'Anonymous')
        self.assertIsInstance(post.posted, datetime)
        self.assertIn('Пост', repr(post))

    # ---------- Create ----------

    def test_create_form_page(self):
        response = self.client.get('/post/create')
        self.assertEqual(response.status_code, 200)
        html = self.text(response)
        for field in ('title', 'content', 'enabled', 'publish_date', 'category'):
            self.assertIn(f'name="{field}"', html)
        self.assertNotIn('name="author"', html)

    def test_create_post(self):
        response = self.client.post('/post/create', data=post_data())
        self.assertEqual(response.status_code, 302)  # PRG
        self.assertTrue(response.location.endswith('/post'))

        post = db.session.scalar(db.select(Post))
        self.assertEqual(post.title, 'Перший пост')
        self.assertEqual(post.category, 'news')
        self.assertEqual(post.posted, datetime(2026, 11, 7, 12, 30))
        self.assertEqual(post.author, 'Anonymous')
        self.assertTrue(post.is_active)
        self.assertIn('Post added successfully', self.text(self.client.get('/post')))

    def test_create_post_author_from_session(self):
        with self.client.session_transaction() as sess:
            sess['username'] = 'admin'
        self.client.post('/post/create', data=post_data())
        self.assertEqual(db.session.scalar(db.select(Post)).author, 'admin')

    def test_create_post_validation(self):
        response = self.client.post('/post/create', data=post_data(title=''))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Вкажіть заголовок', self.text(response))
        self.assertEqual(db.session.scalars(db.select(Post)).all(), [])

    # ---------- Read ----------

    def test_list_shows_only_active_posts_newest_first(self):
        self.add(title='Старий', posted=datetime(2025, 1, 1))
        self.add(title='Новий', posted=datetime(2026, 1, 1))
        self.add(title='Прихований', is_active=False)
        html = self.text(self.client.get('/post'))
        self.assertIn('Старий', html)
        self.assertNotIn('Прихований', html)
        self.assertLess(html.index('Новий'), html.index('Старий'))
        self.assertIn('img/default.jpg', html)
        self.assertIn('Add Post', html)

    def test_list_truncates_content(self):
        self.add(content='a' * 100 + 'ХВІСТ')
        self.assertNotIn('ХВІСТ', self.text(self.client.get('/post')))

    def test_detail_post(self):
        post = self.add(title='Деталі', content='Повний текст', author='admin')
        response = self.client.get(f'/post/{post.id}')
        self.assertEqual(response.status_code, 200)
        html = self.text(response)
        for text in ('Деталі', 'Повний текст', 'admin', 'Технології', 'Edit', 'Delete'):
            self.assertIn(text, html)

    def test_detail_not_found(self):
        response = self.client.get('/post/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Сторінку не знайдено', self.text(response))

    def test_unknown_url_404(self):
        self.assertEqual(self.client.get('/no-such-page').status_code, 404)

    # ---------- Update ----------

    def test_edit_form_prefilled(self):
        post = self.add(title='Старий заголовок', posted=datetime(2026, 5, 1, 9, 15))
        html = self.text(self.client.get(f'/post/{post.id}/update'))
        self.assertIn('value="Старий заголовок"', html)
        self.assertIn('value="2026-05-01T09:15"', html)

    def test_update_post(self):
        post = self.add()
        response = self.client.post(f'/post/{post.id}/update',
                                    data=post_data(title='Оновлено', category='other',
                                                   publish_date='2026-01-02T03:04'))
        self.assertEqual(response.status_code, 302)
        db.session.refresh(post)
        self.assertEqual(post.title, 'Оновлено')
        self.assertEqual(post.category, 'other')
        self.assertEqual(post.posted, datetime(2026, 1, 2, 3, 4))
        self.assertIn('Post updated successfully', self.text(self.client.get(response.location)))

    def test_update_can_hide_post(self):
        post = self.add()
        self.client.post(f'/post/{post.id}/update', data=post_data(enabled=''))
        db.session.refresh(post)
        self.assertFalse(post.is_active)

    def test_update_not_found(self):
        self.assertEqual(self.client.get('/post/42/update').status_code, 404)

    # ---------- Delete ----------

    def test_delete_confirm_page(self):
        post = self.add(title='На видалення')
        response = self.client.get(f'/post/{post.id}/delete')
        self.assertEqual(response.status_code, 200)
        self.assertIn('На видалення', self.text(response))
        self.assertIsNotNone(db.session.get(Post, post.id))  # GET нічого не видаляє

    def test_delete_post(self):
        post = self.add()
        post_id = post.id
        response = self.client.post(f'/post/{post_id}/delete')
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(db.session.get(Post, post_id))
        self.assertIn('видалено', self.text(self.client.get('/post')))

    def test_delete_not_found(self):
        self.assertEqual(self.client.post('/post/7/delete').status_code, 404)


if __name__ == '__main__':
    unittest.main()
