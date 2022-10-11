from flask import Blueprint, render_template

bp = Blueprint('api', __name__)

from setup.api import users, errors, tokens

@bp.route('/')
def home():
    return render_template('home.html')