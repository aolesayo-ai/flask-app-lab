from flask_login import UserMixin
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import bcrypt, db, login_manager


class User(UserMixin, db.Model):
    """Користувач сайту. UserMixin додає is_authenticated, is_active, get_id() тощо."""
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)  # тут зберігається ХЕШ

    # Зв'язок з постами (один до багатьох)
    posts: Mapped[list['Post']] = relationship(back_populates='user', cascade='all, delete-orphan')

    def set_password(self, raw_password: str) -> None:
        """Хешує пароль (bcrypt) і зберігає лише хеш."""
        self.password = bcrypt.generate_password_hash(raw_password).decode('utf-8')

    def check_password(self, raw_password: str) -> bool:
        """Порівнює введений пароль із хешем у БД."""
        try:
            return bcrypt.check_password_hash(self.password, raw_password)
        except ValueError:
            # у БД не bcrypt-хеш (наприклад, пароль, збережений відкритим текстом)
            return False

    def __repr__(self) -> str:
        return f'<User {self.username!r} ({self.email})>'


@login_manager.user_loader
def load_user(user_id: str):
    """Flask-Login зберігає в сесії id як рядок, тому перетворюємо на int."""
    return db.session.get(User, int(user_id))
