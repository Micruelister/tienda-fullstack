from flask import Blueprint, jsonify, request, session
from sqlalchemy import or_

from ..extensions import db, bcrypt
from ..models import User
from .. import api_login_required

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Username, email, and password are required"}), 400

    username, email, password = data['username'], data['email'], data['password']

    if User.query.filter(or_(User.username == username, User.email == email)).first():
        return jsonify({"message": "Username or email already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email and password are required"}), 400

    login_identity, password = data['email'], data['password']
    user = User.query.filter(or_(User.username == login_identity, User.email == login_identity)).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        session.modified = True
        return jsonify({"message": "Login successful!", "user": user.to_dict()}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logout successful"}), 200

@auth_bp.route('/user/profile', methods=['GET'])
@api_login_required
def get_user_profile():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

@auth_bp.route('/user/profile', methods=['PUT'])
@api_login_required
def update_user_profile():
    user_id = session.get('user_id')
    user_to_update = User.query.get_or_404(user_id)

    data = request.get_json()
    new_username = data.get('username')
    new_email = data.get('email')
    new_phone_number = data.get('phoneNumber')

    if new_username != user_to_update.username and User.query.filter_by(username=new_username).first():
        return jsonify({"message": "Username already taken"}), 409
    if new_email != user_to_update.email and User.query.filter_by(email=new_email).first():
        return jsonify({"message": "Email already registered"}), 409

    user_to_update.username = new_username
    user_to_update.email = new_email
    user_to_update.phone_number = new_phone_number

    db.session.commit()

    return jsonify({"message": "Profile updated successfully!", "user": user_to_update.to_dict()}), 200

@auth_bp.route('/user/change-password', methods=['POST'])
@api_login_required
def change_password():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)

    data = request.get_json()
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
    confirm_password = data.get('confirmPassword')

    if not all([current_password, new_password, confirm_password]):
        return jsonify({"message": "All fields are required"}), 400

    if not bcrypt.check_password_hash(user.password_hash, current_password):
        return jsonify({"message": "Incorrect current password"}), 403

    if bcrypt.check_password_hash(user.password_hash, new_password):
        return jsonify({"message": "New password cannot be the same as the current password"}), 400

    if new_password != confirm_password:
        return jsonify({"message": "New passwords do not match"}), 400

    user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    return jsonify({"message": "Password updated successfully!"}), 200
