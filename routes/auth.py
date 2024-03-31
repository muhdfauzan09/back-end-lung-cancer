import jwt
import base64
from db import db
from flask import Blueprint, request, jsonify
from models.userModel import user_detail_model
from models.departmentModel import department_detail_model

auth = Blueprint('auth', __name__)

# Register
@auth.route('/user/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()  # get Post data from FronEnd

        # Check if the email already exists or not
        existing_user = user_detail_model.query.filter_by(
            user_email=data['email']).first()
        if existing_user:
            return jsonify({
                "message": "The email is already registered.",
                "status": 400
            }), 400

        password = data['password']
        encrypted_password = base64.b64encode(password.encode('utf-8'))

        # Create a new user
        new_user = user_detail_model(
            role_id=2,
            user_first_name=data['firstName'],
            user_last_name=data['lastName'],
            user_email=data['email'],
            user_password=encrypted_password,
            user_phone_number=data['phoneNumber'],
            user_status="Pending"
        )

        db.session.add(new_user)
        db.session.commit()
        last_id = new_user.user_id  # Get the last inserted user ID

        # Create new department
        new_department = department_detail_model(
            department_type_id=data['department'],
            user_id=last_id,
            department_name=data['departmentName'],
            department_address=data['address1'],
            city=data['city'],
            state=data['state'],
            zipcode=data['zipCode'],
        )

        db.session.add(new_department)
        db.session.commit()

        return jsonify({
            "status": 200,
            "message": "Your registration has been successful.",
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": 500,
            "error": str(e),
        }), 500


# Login
@auth.route('/user/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = user_detail_model.query.filter_by(user_email=email).first()

        if not user:
            return jsonify({
                "msg": "User does not exist",
                "code": 400,
            }), 400

        user_email = user.user_email
        user_password = user.user_password
        user_status = user.user_status
        user_role_id = user.role_id
        decrypted_password = base64.b64decode(user_password).decode("utf-8")
        secret_key = "secret_key"

        if user_role_id == 2 and decrypted_password == password and user_email == email and  user_status == "Approved":
            access_token = jwt.encode({
                'user_id': user.user_id,
                'department_id': user.department_detail.department_id,
                'role': user.role_id,
                'email': user.user_email,
            }, secret_key, algorithm='HS256')

            return jsonify({
                "msg": "Successly Login",
                "code": 200,
                "access_token": access_token,
                "role_id": user.role_id
            }), 200
        
        if user_role_id == 1 and user_email == email and decrypted_password == password:
            access_token = jwt.encode({
                'user_id': user.user_id,
                'role': user.role_id,
                'email': user.user_email,
            }, secret_key, algorithm='HS256')

            return jsonify({
                "msg": "Successly Login",
                "code": 200,
                "access_token": access_token,
                "role_id": user.role_id
            }), 200
        
        else:
            return jsonify({
                "msg": "Your Account does not verified yet",
                "code": 401,
            }), 401

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": 500,
            "error": str(e),
        }), 500
