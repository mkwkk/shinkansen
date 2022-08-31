from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db
from .langconfig import switch_language
import locale

homepage = Blueprint("homepage", __name__, url_prefix='/')
languages = switch_language()
# global current_lang

@homepage.before_request
@homepage.route('/')
def set_language_default():
    language = request.args.get('language')
    if language is not None:
        session['language'] = language
    else:
      session['language'] = locale.getlocale()[0]
    language = session.get('language')
    return render_template('home.html', language=language, user=current_user, **languages[language])
