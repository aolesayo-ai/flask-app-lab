from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Зв'язок з постами (один до багатьох)
    posts: Mapped[list['Post']] = relationship(back_populates='user', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'<User {self.username!r} ({self.email})>'
