from datetime import datetime

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
    author = db.Column(db.String(20), default='Anonymous', server_default='Anonymous')

    def __repr__(self):
        return f'<Post id={self.id} title={self.title!r} category={self.category}>'
