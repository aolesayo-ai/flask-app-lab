from decimal import Decimal

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileSize
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, ValidationError

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 МБ

CATEGORY_CHOICES = [
    ('', '— Оберіть категорію —'),
    ('electronics', 'Електроніка'),
    ('books', 'Книги'),
    ('clothes', 'Одяг'),
    ('home', 'Дім і сад'),
    ('sport', 'Спорт'),
    ('other', 'Інше'),
]
CATEGORY_LABELS = dict(CATEGORY_CHOICES)


def max_two_decimals(form, field):
    if field.data is not None and field.data.as_tuple().exponent < -2:
        raise ValidationError('Ціна має містити не більше двох знаків після коми')


class ProductForm(FlaskForm):
    name = StringField('Назва', validators=[
        DataRequired(message='Вкажіть назву'),
        Length(min=3, max=100, message='Назва: від 3 до 100 символів'),
    ])
    content = TextAreaField('Опис', validators=[
        DataRequired(message='Додайте опис'),
        Length(max=2000),
    ], render_kw={'rows': 5, 'cols': 40})
    price = DecimalField('Ціна, $', places=2, validators=[
        InputRequired(message='Вкажіть ціну'),
        NumberRange(min=Decimal('0.01'), message='Ціна має бути додатною'),
        max_two_decimals,
    ], render_kw={'step': '0.01', 'min': '0.01'})
    category = SelectField('Категорія', choices=CATEGORY_CHOICES,
                           validators=[DataRequired(message='Оберіть категорію')])
    quantity = IntegerField('Кількість', validators=[
        InputRequired(message='Вкажіть кількість'),
        NumberRange(min=0, message="Кількість не може бути від'ємною"),
    ], render_kw={'min': '0'})
    image = FileField('Зображення (PNG, JPG, JPEG, до 2 МБ)', validators=[
        FileAllowed(ALLOWED_EXTENSIONS, 'Дозволені лише PNG, JPG, JPEG'),
        FileSize(max_size=MAX_IMAGE_SIZE, message='Файл більший за 2 МБ'),
    ])
    submit = SubmitField('Зберегти')


class DeleteForm(FlaskForm):
    """Порожня форма лише для CSRF-токена кнопки видалення."""
    submit = SubmitField('Видалити')
