from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db

CATEGORIES = ('news', 'publication', 'tech', 'other')


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    posted = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.Enum(*CATEGORIES, name='post_category'), default='other')
    is_active = db.Column(db.Boolean, default=True, server_default=db.true())

    # Лабораторна 8: автор поста — користувач (зв'язок «один до багатьох»)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='posts')

    # Лабораторна 8: теги поста (зв'язок «багато до багатьох»)
    tags: Mapped[list['Tag']] = relationship(secondary='post_tags', back_populates='posts')

    def __repr__(self):
        return f'<Post id={self.id} title={self.title!r} category={self.category}>'


# Асоціативна таблиця для зв'язку «багато до багатьох» Post <-> Tag
post_tags = db.Table(
    'post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
)


class Tag(db.Model):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)

    # Зв'язок «багато до багатьох» з постами
    posts: Mapped[list['Post']] = relationship(secondary=post_tags, back_populates='tags')

    def __repr__(self):
        return f'<Tag {self.name}>'
