from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length

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
    submit = SubmitField('Зберегти')


class DeleteForm(FlaskForm):
    """Порожня форма лише для CSRF-токена під час видалення."""
    submit = SubmitField('Так, видалити')
