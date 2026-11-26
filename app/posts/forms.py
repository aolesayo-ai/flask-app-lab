from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import (BooleanField, SelectField, SelectMultipleField, StringField, SubmitField,
                     TextAreaField)
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length

from app import db

CATEGORY_CHOICES = [
    ('news', 'Новина'),
    ('publication', 'Публікація'),
    ('tech', 'Технології'),
    ('other', 'Інше'),
]
CATEGORY_LABELS = dict(CATEGORY_CHOICES)


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[
        DataRequired(message='Вкажіть заголовок'),
        Length(min=3, max=150, message='Заголовок: від 3 до 150 символів'),
    ])
    content = TextAreaField('Текст поста', validators=[
        DataRequired(message='Додайте текст поста'),
    ], render_kw={'rows': 6})
    enabled = BooleanField('Опублікувати (пост видно на сайті)', default=True)
    publish_date = DateTimeLocalField('Дата публікації', format='%Y-%m-%dT%H:%M',
                                      default=datetime.now,
                                      validators=[DataRequired(message='Вкажіть дату')])
    category = SelectField('Категорія', choices=CATEGORY_CHOICES, default='other')
    # Лабораторна 8: автор і теги вибираються зі списків, завантажених із БД
    author_id = SelectField('Автор', coerce=int,
                            validators=[DataRequired(message='Оберіть автора')])
    tags = SelectMultipleField('Теги', coerce=int, render_kw={'size': 4})
    submit = SubmitField('Зберегти')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.users.models import User
        from .models import Tag
        # SQLAlchemy 2.0: select() + scalars() замість застарілого User.query
        users = db.session.scalars(db.select(User).order_by(User.id)).all()
        tags = db.session.scalars(db.select(Tag).order_by(Tag.name)).all()
        self.author_id.choices = [(u.id, u.username) for u in users]
        self.tags.choices = [(t.id, t.name) for t in tags]


class DeleteForm(FlaskForm):
    """Порожня форма лише для CSRF-токена під час видалення."""
    submit = SubmitField('Так, видалити')
