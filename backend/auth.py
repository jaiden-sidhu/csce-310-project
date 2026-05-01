"""
Authentication and authorization utilities
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FLASK_SECRET_KEY


def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    try:
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        if isinstance(password, str):
            password = password.encode('utf-8')
        return bcrypt.checkpw(password, hashed_password)
    except ValueError:
        return False


def generate_token(user_id, role, expires_in_hours=24):
    """Generate JWT token for authentication"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, FLASK_SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, FLASK_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def check_token_validity(token):
    """Check if token is valid and not expired"""
    payload = verify_token(token)
    return payload is not None
