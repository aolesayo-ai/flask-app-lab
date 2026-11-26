from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError

from app import db

from .models import User


class RegistrationForm(FlaskForm):
    username = StringField('Ім\'я користувача', validators=[
        DataRequired(message="Це поле обов'язкове"),
        Length(min=4, max=14, message='Ім\'я має бути довжиною від 4 до 14 символів'),
        Regexp(r'^[A-Za-z][A-Za-z0-9_.]*$',
               message='Ім\'я починається з літери й містить лише латинські літери, цифри, крапки або _'),
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Це поле обов'язкове"),
        Email(message='Введіть коректну email-адресу'),
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Це поле обов'язкове"),
        Length(min=6, message='Пароль має бути не коротшим за 6 символів'),
    ])
    confirm_password = PasswordField('Підтвердження пароля', validators=[
        DataRequired(message="Це поле обов'язкове"),
        EqualTo('password', message='Паролі не збігаються'),
    ])
    submit = SubmitField('Зареєструватися')

    # Перевірка унікальності у БД (WTForms викликає validate_<поле> автоматично)
    def validate_username(self, field):
        if db.session.scalar(db.select(User).where(User.username == field.data)):
            raise ValidationError('Користувач із таким іменем вже існує.')

    def validate_email(self, field):
        if db.session.scalar(db.select(User).where(User.email == field.data.lower())):
            raise ValidationError('Цей email вже зареєстровано.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Це поле обов'язкове"),
        Email(message='Введіть коректну email-адресу'),
    ])
    password = PasswordField('Пароль', validators=[DataRequired(message="Це поле обов'язкове")])
    remember = BooleanField("Запам'ятати мене")
    submit = SubmitField('Увійти')
