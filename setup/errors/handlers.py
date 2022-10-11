from flask import render_template, request
from setup.errors import bp
from setup import db
from setup.api.errors import error_response as api_error_response

def wants_json_response():
    # If client prefers json over html
    return request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']

@bp.app_errorhandler(404)
def not_found_error(error):
    return api_error_response(404)

@bp.app_errorhandler(413)
def too_large_error(error):
    return api_error_response(413, "Image should not be larger than 500 KB")

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return api_error_response(500)