from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from setup.models import User
from setup.api.errors import error_response

token_auth = HTTPTokenAuth()


def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user


def basic_auth_error(status):
    return error_response(status)

@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None

@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)
