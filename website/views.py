from crypt import methods
from hashlib import new
from unicodedata import category, name
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db
from .langconfig import switch_language
from sqlalchemy import desc

views = Blueprint("views", __name__, url_prefix='/')
languages = switch_language()
# global current_lang


# @views.route('/lang=<language>', methods=['GET'])
# def set_language(language):
#     session['language'] = language
#     return render_template('home.html', user=current_user, **languages[language])

@views.route("/home/")
# @login_required
def home():
    if 'language' in request.args:
        language = request.args.get('language')
        if language is not None:
            session['language'] = language
    language = session.get('language')
    posts = Post.query.all()
    print(current_user)
    return render_template("home.html", language=language, user=current_user, posts=posts, **languages[language])

# profile
@views.route("/profile/<username>/")
def profile(username):
    if 'language' in request.args:
        language = request.args.get('language')
        if language is not None:
            session['language'] = language
    language = session.get('language')
    user = User.query.filter_by(username=username).first()
    categories = Post.query.filter_by(author=user.id).with_entities(Post.category).distinct().all()
    newCategories = []
    if(len(categories) > 0):
        for item in categories:
            newItem = str(item).replace('(', '').replace(')', '').replace('\'', '').replace(',', '')
            newCategories.append(newItem)
    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for("views.home"))
    posts = user.posts
    if(len(posts) <= 0):
        category = "現在投稿はありません"
    else:
        category = "All Post"
    return render_template("profile.html", language=language, **languages[language], user=current_user, posts=posts, username=username, user_post=user, categories=newCategories, category=category)

@views.route("/update-profile/<username>/", methods=['POST', 'GET'])
@login_required
def update_profile(username):
    if 'language' in request.args:
        language = request.args.get('language')
        if language is not None:
            session['language'] = language
    language = session.get('language')
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('No user with that username exists.')
        return redirect(url_for("views.home"))
    elif username == current_user.username:
        if request.method == 'POST':
            user.age = request.form.get("age")
            user.gender = request.form.get("gender")
            user.work = request.form.get("work")
            user.country = request.form.get("country")
            user.avatar = request.form.get("avatar")
            if len(user.age) > 130:
                flash('Your age is invalid.', category='error')
            elif len(user.work) < 2:
                flash('Your work is invalid.', category='error')
            else:
                db.session.merge(user)
                db.session.commit()
                flash('User Update!')
                return redirect(url_for('views.profile', username=username))
        return render_template("update_profile.html", language=language, **languages[language], user=current_user)
    elif username != current_user.username:
        flash('User doesn\'t have edit access.')
        return redirect(url_for('views.profile'))
# end profile


# category
@views.route("/home/<category>", methods=['GET', 'POST'])
def show_category(category):
    if 'language' in request.args:
        language = request.args.get('language')
        if language is not None:
            session['language'] = language
    language = session.get('language')
    if request.method == "POST":
        searchTitle = request.form.get("searchTitle")
        searchT = "%{}%".format(searchTitle)
        posts = Post.query.filter_by(category=category).filter(Post.title.like(searchT)).all()
        return render_template("posts.html", language=language, **languages[language], user=current_user, category=category, posts=posts, searchTitle=searchTitle)
    else:
        posts = Post.query.filter_by(category=category,).order_by(desc(Post.date_created)).all()
    return render_template("posts.html", language=language, **languages[language], user=current_user, category=category, posts=posts)

# end category

# post
@views.route("/home/<category>/create-post/", methods=['GET', 'POST'])
@login_required
def create_post(category):
    if 'language' in request.args:
        language = request.args.get('language')
        if language is not None:
            session['language'] = language
    language = session.get('language')
    if request.method == "POST":
        text = request.form.get('text').replace('\n', '<br>')
        title = request.form.get('title')
        if not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text,category=category,title=title,author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
        return redirect(url_for("views.show_category", category=category))
    return render_template('create_post.html', category=category, language=language, user=current_user, **languages[language])

@views.route("/home/<category>/delete-post/<id>")
@login_required
def delete_post(category, id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for("views.show_category", category=category, id=id))

@views.route("/home/<category>/update-post/<post_id>", methods=['GET', 'POST'])
@login_required
def update_post(category, post_id):
    if 'language' in request.args:
        language = request.args.get('language')
        if language is not None:
            session['language'] = language
    language = session.get('language')
    post = Post.query.filter_by(id=post_id).first()
    if request.method == "POST":
        if not post:
            flash("Post does not exist.", category='error')
        elif current_user.id != post.author:
            flash('You do not have permission to delete this post.', category='error')
        else:
            post.text = request.form['text']
            post.title = request.form['title']
            db.session.merge(post)
            db.session.commit()
            flash('Post updated', category='success')
        return redirect(url_for("views.show_category", category=category, id=post_id))
    return render_template('update_post.html', category=category,  post_update=post, language=language, user=current_user, **languages[language])

# end post

# comment

@views.route("/home/<category>/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(category, post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for("views.show_category", category=category, id=post_id))


@views.route("/home/<category>/delete-comment/<comment_id>")
@login_required
def delete_comment(category, comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for("views.show_category", category=category, id=comment_id))


# @views.route("/home/<category>/update-comment/<comment_id>", methods=['GET', 'POST'])
# @login_required
# def update_post(category, comment_id):
#     if 'language' in request.args:
#         language = request.args.get('language')
#         if language is not None:
#             session['language'] = language
#     language = session.get('language')
#     comment = Comment.query.filter_by(id=comment_id).first()
#     if request.method == "POST":
#         if not comment:
#             flash("Comment does not exist.", category='error')
#         elif current_user.id != comment.author:
#             flash('You do not have permission to delete this post.', category='error')
#         else:
#             comment.text = request.form['text']
#             db.session.merge(comment)
#             db.session.commit()
#             flash('Post updated', category='success')
#         return redirect(url_for("views.show_category", category=category, id=post_id))
#     return render_template('update_post.html', category=category,  post=post, language=language, user=current_user, **languages[language])

# # end comment

# like post
@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})
# end like
