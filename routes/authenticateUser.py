from flask import Blueprint, request, jsonify
from models.userModel import user_detail_model
from functools import wraps
import jwt

auth = Blueprint("auth", __name__)


# Token Validation API (USER)
def token_required_user(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', None)

        if not token:
            return jsonify({
                "message": "Authentication Token is missing!",
                "status": 401,
            }), 401

        try:
            key = "secret_key"
            token = token.split(" ")[1]
            decoded_token = jwt.decode(token, key, algorithms="HS256")

            user_data = user_detail_model.query.filter_by(
                user_id=decoded_token['user_id'],
                role_id=2,
                user_email=decoded_token['email']
            ).first()

            if not user_data:
                return jsonify({
                    "message": "Invalid Authentication token",
                    "status": 401,
                }), 401

            user = {
                "user_id": decoded_token['user_id'],
                "department_id": decoded_token['department_id'],
                "role": decoded_token['role'],
                "email": decoded_token['email']
            }

        except jwt.ExpiredSignatureError:
            return jsonify({
                "message": "Token has expired",
                "status": 403,
            }), 403

        except jwt.InvalidTokenError as e:
            return jsonify({
                "message": "Invalid token",
                "status": 401,
                "error": str(e)
            }), 401

        return func(user, *args, **kwargs)

    return decorated


# Token Validation API (ADMIN)
def token_required_admin(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', None)

        if not token:
            return jsonify({
                "message": "Authentication Token is missing!",
                "status": 401,
            }), 401

        try:
            key = "secret_key"
            token = token.split(" ")[1]
            decoded_token = jwt.decode(token, key, algorithms="HS256")

            user_data = user_detail_model.query.filter_by(
                user_id=decoded_token['user_id'],
                role_id=1,
                user_email=decoded_token['email']
            ).first()

            if not user_data:
                return jsonify({
                    "message": "Invalid Authentication token",
                    "status": 401,
                }), 401

            user = {
                "id": decoded_token['user_id'],
                "role": decoded_token['role'],
            }

        except jwt.ExpiredSignatureError:
            return jsonify({
                "message": "Token has expired",
                "status": 401,
            }), 401

        except jwt.InvalidTokenError as e:
            return jsonify({
                "message": "Invalid token",
                "status": 401,
                "error": str(e)
            }), 401

        return func(user, *args, **kwargs)

    return decorated
