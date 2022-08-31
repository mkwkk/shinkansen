from pickle import NONE
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .langconfig import switch_language

auth = Blueprint("auth", __name__,url_prefix='/')
languages = switch_language()

@auth.route("/login", methods=['GET', 'POST'])
def login():
    language = session.get('language')
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user, **languages[language])


@auth.route("/sign-up/", methods=['GET', 'POST'])
def sign_up():
    language = request.args.get('language')
    if language is not None:
        session['language'] = language
    language = session.get('language')
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        age = request.form.get("age")
        gender = request.form.get("gender")
        work = request.form.get("work")
        country = request.form.get("country")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Password don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(age) > 130:
            flash('Your age is invalid.', category='error')
        elif len(work) < 2:
            flash('Your work is invalid.', category='error')
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            new_user = User(email=email, username=username, age=age,
            gender=gender, work=work, country=country, password=generate_password_hash(
            password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            return render_template("home.html", user=current_user, **languages[language])
    return render_template("signup.html", user=current_user, **languages[language])


@auth.route("/logout/")
@login_required
def logout():
    language = request.args.get('language')
    if language is not None:
        session['language'] = language
    language = session.get('language')
    logout_user()
    return render_template("home.html", user=current_user, **languages[language])
