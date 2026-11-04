from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(message="Це поле є обов'язковим"),
        Length(min=4, max=10, message="Довжина імені має бути від 4 до 10 символів")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Це поле є обов'язковим"),
        Email(message="Введіть коректну email-адресу")
    ])
    phone = StringField('Phone', validators=[
        DataRequired(message="Це поле є обов'язковим"),
        Regexp(r'^\+380\d{9}$', message="Формат телефону: +380XXXXXXXXX")
    ])
    subject = SelectField('Subject', choices=[
        ('', 'Оберіть тему...'),
        ('general', 'Загальне питання'),
        ('support', 'Технічна підтримка'),
        ('feedback', 'Відгук або пропозиція')
    ], validators=[DataRequired(message="Будь ласка, оберіть тему звернення")])
    message = TextAreaField('Message', validators=[
        DataRequired(message="Це поле є обов'язковим"),
        Length(max=500, message="Повідомлення не може перевищувати 500 символів")
    ])
    submit = SubmitField('Send Message')