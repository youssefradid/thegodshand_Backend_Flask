from flask import jsonify, request, url_for, current_app
from setup.models import User, Orphanage, Message, Donation
from setup.api import bp
from setup import db
from setup.api.errors import bad_request, error_response
from setup.api.auth import token_auth
from setup.api.tokens import save_file, delete_file
import logging

@bp.route('/user/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())

@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')# under items
    return jsonify(data)

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('Must include username, email and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('Please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('Please use a different email address')
    user = User()
    user.from_dict(data)
    db.session.add(user)
    db.session.commit()
    final_data = user.to_dict()
    final_data['token'] = user.get_token()
    response = jsonify(final_data)
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response

@bp.route('/user/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    current_app.logger.info(id)
    if token_auth.current_user().id != id:
        return error_response(403, "You are not allowed to edit another user's data")
    user = User.query.get_or_404(id)
    current_app.logger.info(user)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
        User.query.filter_by(username=data['username']).first():
        return bad_request('Please use a different username.Username already taken')
    if 'email' in data and data['email'] != user.email and \
        User.query.filter_by(email=data['email']).first():
        return bad_request('Please use a different email address. Email address already taken')
    user.from_dict(data)
    db.session.commit()
    return jsonify(user.to_dict())

@bp.route('/user/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_user(id):
    if token_auth.current_user().id != id:
        return error_response(403, 'You are not allowed to delete another user')
    user = User.query.get_or_404(id)
    name = user.name
    db.session.delete(user)
    db.session.commit()
    return jsonify({'deleted_user': name})

@bp.route('/orphanages', methods=['GET'])
def get_orphanages():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 100, type=int), 100)
    orphs = Orphanage.to_collection_dict(Orphanage.query, page, per_page, 'api.get_orphanages')# under items
    current_app.logger.setLevel(logging.INFO)
    current_app.logger.info(orphs)
    return jsonify(orphs)

@bp.route('/orphanages', methods=['POST'])
@token_auth.login_required
def create_orphanage():
    data = request.get_json() or {}
    columns = ['name', 'email', 'students', 'phone_no', 'location', 'activities', 'paypal_info', 'social_media_links',
               'story', 'money_uses', 'photos_links', 'bank_info', 'actId', 'acttype', 'country', 'good_work',
               'monthly_donation', 'registration_certificate', 'heading','blog_link']
    for field in columns:
        if field not in data:
            return bad_request('Must include all required fields')
    if Orphanage.query.filter_by(name=data['name']).first():
        return bad_request('Please use a different Orphanage name')
    if Orphanage.query.filter_by(email=data['email']).first():
        return bad_request('Please use a different email address')
    if not token_auth.current_user().is_admin: # if the user is not an admin
        return error_response(401, 'Admin status is required to create an orphanage')
    orph = Orphanage()
    orph.from_dict(data)
    db.session.add(orph)
    db.session.commit()
    response = jsonify(orph.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_orphanage', id=orph.id)
    return response

@bp.route('/orphanage/<int:id>', methods=['GET'])
def get_orphanage(id):
    return jsonify(Orphanage.query.get_or_404(id).to_dict())


@bp.route('/orphanage/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_orphanage(id):
    orph = Orphanage.query.get_or_404(id)
    data = request.get_json() or {}
    if 'name' in data and data['name'] != orph.name and \
        Orphanage.query.filter_by(name=data['name']).first():
        return bad_request('Please use a different Orphanage name')
    if 'email' in data and data['email'] != orph.email and \
        Orphanage.query.filter_by(email=data['email']).first():
        return bad_request('Please use a different email address')
    if not token_auth.current_user().is_admin: # if the user is not an admin
        return error_response(401, 'Admin status is required to update an orphanage')
    orph.from_dict(data)
    db.session.commit()
    return jsonify(orph.to_dict())

@bp.route('/orphanage/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_orphanage(id):
    orph = Orphanage.query.get_or_404(id)
    if not token_auth.current_user().is_admin: # if the user is not an admin
        return error_response(401, 'Admin status is required to delete an orphanage')
    name = orph.name
    db.session.delete(orph)
    db.session.commit()
    return jsonify({'deleted_orphanage': name})

@bp.route('/messages', methods=['POST'])
def contact_us():
    data = request.get_json() or {}
    for field in ['first_name', 'last_name','email', 'phone_no', 'content']:
        if field not in data:
            return bad_request('Must include all required fields')
    message = Message()
    message.from_dict(data)
    db.session.add(message)
    db.session.commit()
    response = jsonify({'status': 'Message successfully sent'})
    response.status_code = 201
    return response

@bp.route('/messages', methods=['GET'])
def get_messages():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    messages = Message.to_collection_dict(Message.query, page, per_page, 'api.get_messages')# under items
    return jsonify(messages)

@bp.post('/donations')
def add_donation():
    data = request.get_json() or {}
    for field in ['username', 'orphanage_name', 'amount']:
        if field not in data:
            return bad_request('Must include all required fields')
    # If orphanage or user not found, return a bad request
    user = User.query.filter_by(username=data['username']).first()
    orph = Orphanage.query.filter_by(name=data['orphanage_name']).first()
    if not user:
        return bad_request('User not found')
    if not orph:
        return bad_request('Orphanage not found')
    donation = Donation(amount=data['amount'], donor=user, recipient=orph)
    db.session.add(donation)
    db.session.commit()
    response = jsonify({'status': 'Donation successfully added'})
    response.status_code = 201
    return response

@bp.route('/orphanage_donations/<int:id>')
@token_auth.login_required
def get_donations(id):
    orph = Orphanage.query.get_or_404(id)
    if not token_auth.current_user().is_admin: # if the user is not an admin
        return error_response(401, "Admin status is required to view an orphanage's donations")
    # convert this orphanage's donations to dict
    donations = [each.to_dict() for each in orph.donations]
    result = {'donations': donations, 'orphanage_name': orph.name}
    return jsonify(result)

@bp.post('/image_upload')
def image_upload():
    _file = request.files['file']
    filepath = save_file(_file)
    if filepath == "Not allowed":
        return error_response(415, "File is not an image of type 'png','jpg','jpeg' or 'gif'.")
    response = jsonify({'filepath': filepath})
    response.status_code = 201
    return response

@bp.route('/image_delete', methods=['POST'])
@token_auth.login_required
def delete_image():
    if not token_auth.current_user().is_admin:
        return error_response(401, "Only an admin is allowed to delete images")
    data = request.get_json() or {}
    filepath = data['filepath']
    filename = delete_file(filepath)
    if filename == "File doesn't exist": 
        file = filepath.split('/')[2] # after static/images
        return error_response(404, f"File {file} does not exist")
    return jsonify({'deleted_file': filename})



    
