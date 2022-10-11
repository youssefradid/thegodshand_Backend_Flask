from flask import jsonify, request, current_app
from setup import db
from setup.api import bp
from setup.api.auth import verify_password, token_auth
from setup.api.errors import error_response
import os
import uuid

@bp.route('/tokens', methods=['POST'])
def get_token():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    user = verify_password(username, password)
    if user is None:
        return error_response(401, "Incorrect username or password")
    data = user.to_dict()
    data['token'] = user.get_token()
    db.session.commit()
    return jsonify(data)

@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file_data):
    f=file_data
    # Check if file is allowed, if not, return 'not allowed'
    if not allowed_file(f.filename):
        return "Not allowed"
    unique = str(uuid.uuid4())
    file_ext = os.path.splitext(f.filename)[1]
    # Use uuid with file extension to save
    filename = unique + file_ext
    target = current_app.config['UPLOAD_FOLDER']
    # There's an error with upload folder abs path
    if not os.path.isdir(target):
        os.mkdir(target)
    file_path = os.path.join(target, filename)
    f.save(file_path)
    output = 'static/images/' + filename
    return output

def delete_file(filepath):
    filename = filepath.split('/')[2] # after static/images
    target = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(target, filename)
    # If file doesn't exists,return an error
    if not os.path.exists(file_path):
        return "File doesn't exist"
    os.remove(file_path)
    return filename