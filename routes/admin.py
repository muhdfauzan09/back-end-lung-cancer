from db import db
from flask import Blueprint, jsonify, request
from routes.authenticateUser import token_required_admin

# Models
from models.userModel import user_detail_model
from models.patientModel import patient_detail_model
from models.departmentModel import department_detail_model

# crete intance
admin = Blueprint('admin', __name__)


# GET Dashboard
@admin.route('/admin/dashboard')
@token_required_admin
def get_dasboard(user):
    try:
        get_user = user_detail_model.query.filter_by(
            user_id=user["id"]).first()
        if not get_user:
            return jsonify({
                "msg": "No User Found",
                "status": 400,
            }), 400

        user_detail = {
            "user_id": get_user.user_id,
            "role_id": get_user.role_id,
            "user_first_name": get_user.user_first_name,
            "user_last_name": get_user.user_last_name,
            "user_email": get_user.user_email,
            "user_phone_number": get_user.user_phone_number,
            "user_status": get_user.user_status,
        }

        return jsonify({
            "msg": "User Found",
            "status": 200,
            "data": user_detail,
        }), 200

    except Exception as e:
        return jsonify({
            "status": 500,
            "error": str(e)
        }), 500


# GET Doctors
@admin.route('/admin/doctor/list', methods=['GET', "POST"])
@token_required_admin
def list_doctor(user):
    try:
        if request.method == "GET":
            get_users = user_detail_model.query.filter_by(role_id=2).all()

            if not get_users:
                return jsonify({
                    "msg": "Users not found",
                    "status": 404,
                }), 404

            doctor_list = []
            for user in get_users:
                user_detail = {
                    "user_id": user.user_id,
                    "role_id": user.role_id,
                    "user_first_name": user.user_first_name,
                    "user_last_name": user.user_last_name,
                    "user_email": user.user_email,
                    "user_phone_number": user.user_phone_number,
                    "user_status": user.user_status,
                }

                if user.department_detail:
                    department = user.department_detail
                    department_details = {
                        "department_id": department.department_id,
                        "department_type_id": department.department_type_id,
                        "department_name": department.department_name,
                        "department_address": department.department_address,
                        "city": department.city,
                        "state": department.state,
                        "zipcode": department.zipcode
                    }
                    doctor_list.append({**user_detail, **department_details})

            return jsonify({
                "msg": "Users Found",
                "data": doctor_list,
                "status": 200,
            }), 200

        if request.method == "POST":
            user = request.get_json()

            if "doctor" not in user or "doctorName" not in user:
                return jsonify({
                    "code": 400,
                    "msg": "Patient name or lung cancer status not provided"
                }), 400

            if user["doctorName"] == "":
                get_user = user_detail_model.query \
                    .join(department_detail_model) \
                    .filter(department_detail_model.department_type_id == user["doctor"]) \
                    .all()
            else:
                search = "%{}%".format(user["doctorName"])
                get_user = user_detail_model.query \
                    .join(department_detail_model) \
                    .filter(user_detail_model.user_first_name.like(search)) \
                    .filter(department_detail_model.department_type_id == user["doctor"]) \
                    .all()

            doctor_list = []
            for user in get_user:
                user_detail = {
                    "user_id": user.user_id,
                    "role_id": user.role_id,
                    "user_first_name": user.user_first_name,
                    "user_last_name": user.user_last_name,
                    "user_email": user.user_email,
                    "user_phone_number": user.user_phone_number,
                    "user_status": user.user_status,
                }

                if user.department_detail:
                    department = user.department_detail
                    department_details = {
                        "department_id": department.department_id,
                        "department_type_id": department.department_type_id,
                        "department_name": department.department_name,
                        "department_address": department.department_address,
                        "city": department.city,
                        "state": department.state,
                        "zipcode": department.zipcode
                    }
                    doctor_list.append({**user_detail, **department_details})

            return jsonify({
                "msg": "Users Found",
                "data": doctor_list,
                "status": 200,
            }), 200

    except Exception as e:
        return jsonify({
            "status": 500,
            "error": str(e),
        }), 500


# GET Departments
@admin.route("/admin/department/list", methods=["GET", "POST"])
@token_required_admin
def list_department(user):
    try:
        if request.method == "GET":
            get_department = department_detail_model.query.all()

            if not get_department:
                return jsonify({
                    "msg": "Departments Not Found",
                    "status": 404
                }), 404

            department_list = []
            for department in get_department:
                department_detail = {
                    "department_id": department.department_id,
                    "department_type_id": department.department_type_id,
                    "user_id": department.user_id,
                    "department_name": department.department_name,
                    "department_address": department.department_address,
                    "city": department.city,
                    "state": department.state,
                    "zipcode": department.zipcode
                }
                department_list.append(department_detail)

            return jsonify({
                "msg": "Departments Found",
                "data": department_list,
                "status": 200
            }), 200

        elif request.method == "POST":
            department = request.get_json()

            if "department" not in department or "departmentName" not in department:
                return jsonify({
                    "code": 400,
                    "msg": "Patient name or lung cancer status not provided"
                }), 400

            if department["departmentName"] == "":
                get_department = department_detail_model.query \
                    .filter(department_detail_model.department_type_id == department["department"]) \
                    .all()
            else:
                search = "%{}%".format(department["departmentName"])
                get_department = department_detail_model.query \
                    .filter(department_detail_model.department_type_id == department["department"]) \
                    .filter(department_detail_model.department_name.like(search)) \
                    .all()

            department_list = []
            for department in get_department:
                department_detail = {
                    "department_id": department.department_id,
                    "department_type_id": department.department_type_id,
                    "user_id": department.user_id,
                    "department_name": department.department_name,
                    "department_address": department.department_address,
                    "city": department.city,
                    "state": department.state,
                    "zipcode": department.zipcode
                }
                department_list.append(department_detail)

            return jsonify({
                "code": 200,
                "data": department_list
            })

    except Exception as e:
        return jsonify({
            "status": 500,
            "error": str(e),
        }), 500


# GET user and department by Id
@admin.route('/admin/view/<int:id>', methods=['GET'])
@token_required_admin
def admin_view(user, id):
    try:
        user = user_detail_model.query.filter_by(user_id=id).first()

        if not user:
            return jsonify({
                "msg": "User not found",
                "status": 404,
            }), 404

        # User Detail
        user_detail = {
            "user_id": user.user_id,
            "role_id": user.role_id,
            "user_first_name": user.user_first_name,
            "user_last_name": user.user_last_name,
            "user_email": user.user_email,
            "user_phone_number": user.user_phone_number,
            "user_status": user.user_status,
        }

        department_details = []
        department = user.department_detail
        department_detail = {
            "department_id": department.department_id,
            "department_type_id": department.department_type_id,
            "user_id": department.user_id,
            "department_name": department.department_name,
            "department_address": department.department_address,
            "city": department.city,
            "state": department.state,
            "zipcode": department.zipcode
        }
        department_details.append(department_detail)

        get_patient = patient_detail_model.query.filter_by(
            department_id=department.department_id).all()
        patient_list = []
        for patient in get_patient:
            patient_detail = {
                "patient_id": patient.patient_id,
                "patient_name": patient.patient_name,
                "patient_gender": patient.patient_gender,
                "patient_address1": patient.patient_address1,
                "patient_address2": patient.patient_address2,
                "patient_postcode": patient.patient_postcode,
                "patient_phone_number": patient.patient_phone_number,
            }

            if patient.feature_detail:
                for feature in patient.feature_detail:
                    feature_detail = {
                        "lung_cancer": feature.lung_cancer
                    }

            patient_list.append({**patient_detail, **feature_detail})

        return jsonify({
            "msg": "User Found",
            "status": 200,
            "user": user_detail,
            "patient": patient_list,
            "department": department_details,
        }), 200

    except Exception as e:
        return jsonify({
            "status": 500,
            "error": str(e),
        }), 500


# POST Status
@admin.route("/admin/doctor/update/<int:id>", methods=["POST"])
@token_required_admin
def update_doctor_status(user, id):
    try:
        get_data = request.get_json()
        status = get_data['status']  # Using get() to avoid KeyErrors

        get_user = user_detail_model.query.filter_by(user_id=id).first()

        if not get_user:
            return jsonify({
                "message": "User Not Found",
                "code": 404,
            }), 404

        # Update Status
        get_user.user_status = status
        db.session.commit()

        return jsonify({
            "message": f"{get_user.user_first_name} {get_user.user_last_name} has been approved",
            "code": 200,
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Internal Server Error",
            "error": str(e),
            "code": 500,
        }), 500


# GET Patient
@admin.route("/admin/get/patient/details/<int:id>", methods=['GET'])
@token_required_admin
def get_patient_details(user, id):
    try:
        get_patient = patient_detail_model.query.filter_by(
            patient_id=id).first()

        if not get_patient:
            return jsonify({
                "code": 404,
                'msg': "No user found"
            }), 404

        patient_list = []
        patient_detail = {
            "patient_id": get_patient.patient_id,
            "patient_name": get_patient.patient_name,
            "patient_gender": get_patient.patient_gender,
            "patient_address1": get_patient.patient_address1,
            "patient_address2": get_patient.patient_address2,
            "patient_postcode": get_patient.patient_postcode,
            "patient_phone_number": get_patient.patient_phone_number,
        }

        if get_patient.feature_detail:
            for feature in get_patient.feature_detail:
                feature_detail = {
                    "smoking": feature.smoking,
                    "yellow_fingers": feature.yellow_fingers,
                    "anxiety": feature.anxiety,
                    "peer_pressure": feature.peer_pressure,
                    "chronic_disease": feature.chronic_disease,
                    "fatigue": feature.fatigue,
                    "allergy": feature.allergy,
                    "wheezing": feature.wheezing,
                    "alcohol_consuming": feature.alcohol_consuming,
                    "coughing": feature.coughing,
                    "shortness_breath": feature.shortness_breath,
                    "swallowing_difficulty": feature.swallowing_difficulty,
                    "chest_pain": feature.chest_pain,
                    "lung_cancer": feature.lung_cancer
                }
                patient_list.append({**patient_detail, **feature_detail})

        return jsonify({
            "code": 200,
            "patient_details": patient_list
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str(e)
        }), 500
