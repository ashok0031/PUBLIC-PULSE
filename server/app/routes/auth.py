from flask import Blueprint, request, jsonify
from app.database import db
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from app.utils.auth import generate_otp, send_verification_email
import time
import logging

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# In-memory OTP store: {email: (otp, expiry_time)}
otp_store = {}

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email required'}), 400
    otp = generate_otp()
    expiry = time.time() + 300  # 5 minutes
    otp_store[email] = (otp, expiry)
    send_verification_email(email, otp)
    return jsonify({'message': 'OTP sent to email'}), 200

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    if not email or not otp:
        return jsonify({'error': 'Email and OTP required'}), 400
    stored = otp_store.get(email)
    if not stored or stored[1] < time.time():
        return jsonify({'error': 'OTP expired or not found'}), 400
    if stored[0] != otp:
        return jsonify({'error': 'Invalid OTP'}), 400
    user = User.query.filter(User.email.ilike(email)).first()
    if not user:
        logging.warning(f'User with email {email} not found during OTP verification.')
        return jsonify({'error': 'User not found'}), 404
    user.email_verified = True
    db.session.commit()
    logging.info(f'User {email} verified successfully.')
    return jsonify({'message': 'Email verified successfully.'}), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter(or_(User.username == username, User.email == email, User.phone == phone)).first():
        return jsonify({'error': 'User already exists'}), 409

    password_hash = generate_password_hash(password)
    user = User(username=username, email=email, phone=phone, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    # Do not mark email_verified here; require OTP verification
    return jsonify({'message': 'User registered successfully, please verify your email.'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('username') or data.get('email') or data.get('phone')
    password = data.get('password')

    if not identifier or not password:
        return jsonify({'error': 'Missing credentials'}), 400

    user = User.query.filter(
        or_(
            User.username == identifier,
            User.email == identifier,
            User.phone == identifier
        )
    ).first()

    if user and check_password_hash(user.password_hash, password):
        if not user.email_verified:
            return jsonify({'error': 'Email not verified'}), 403
        return jsonify({'message': 'Login successful', 'user': {
            'id': user.id, 'username': user.username, 'email': user.email
        }}), 200
    return jsonify({'error': 'Invalid credentials'}), 401 