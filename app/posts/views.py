from flask import flash, redirect, render_template, session, url_for

from app import db

from . import post_bp
from .forms import CATEGORY_LABELS, DeleteForm, PostForm
from .models import Post


@post_bp.app_template_filter('post_category')
def post_category_label(value):
    return CATEGORY_LABELS.get(value, value or '—')


# ---------- Read ----------

@post_bp.route('')
def all_posts():
    stmt = (db.select(Post)
            .where(Post.is_active.is_(True))
            .order_by(Post.posted.desc()))
    posts = db.session.scalars(stmt).all()
    return render_template('posts/posts.html', posts=posts, title='Пости')


@post_bp.route('/<int:id>')
def detail_post(id):
    post = db.get_or_404(Post, id)
    return render_template('posts/detail_post.html', post=post, title=post.title)


# ---------- Create ----------

@post_bp.route('/create', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            is_active=form.enabled.data,
            posted=form.publish_date.data,
            author=session.get('username', 'Anonymous'),  # автор — користувач із сесії
        )
        db.session.add(post)
        db.session.commit()
        flash('Post added successfully', 'success')
        return redirect(url_for('posts.all_posts'))  # PRG

    if form.is_submitted():
        flash('Пост не збережено: виправте помилки у формі.', 'error')
    return render_template('posts/add_post.html', form=form, title='Новий пост', post=None)


# ---------- Update ----------

@post_bp.route('/<int:id>/update', methods=['GET', 'POST'])
def edit_post(id):
    post = db.get_or_404(Post, id)
    form = PostForm(obj=post)

    if form.validate_on_submit():
        form.populate_obj(post)              # title, content, category
        post.posted = form.publish_date.data  # назви полів форми і моделі різні
        post.is_active = form.enabled.data
        db.session.commit()
        flash('Post updated successfully', 'success')
        return redirect(url_for('posts.detail_post', id=post.id))

    if not form.is_submitted():
        # поля з іншими назвами, ніж у моделі, ініціалізуємо вручну
        form.publish_date.data = post.posted
        form.enabled.data = post.is_active
    else:
        flash('Зміни не збережено: виправте помилки у формі.', 'error')
    return render_template('posts/add_post.html', form=form, title='Редагування поста', post=post)


# ---------- Delete ----------

@post_bp.route('/<int:id>/delete', methods=['GET', 'POST'])
def delete_post(id):
    post = db.get_or_404(Post, id)
    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()
        flash(f'Пост «{post.title}» видалено.', 'success')
        return redirect(url_for('posts.all_posts'))

    return render_template('posts/delete_confirm.html', post=post, form=form, title='Видалення поста')
