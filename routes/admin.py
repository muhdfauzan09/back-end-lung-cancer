import base64
from db import db
from datetime import datetime
from collections import defaultdict
from flask_mail import Mail, Message
from flask import Blueprint, jsonify, request
from password_generator import PasswordGenerator
from routes.authenticateUser import token_required_admin

# Models
from models.userModel import user_detail_model
from models.patientModel import patient_detail_model, feature_detail_model
from models.departmentModel import department_detail_model


# crete intance
admin = Blueprint('admin', __name__)
mail = Mail()


# GET Dashboard
@admin.route('/admin/dashboard')
@token_required_admin
def get_dashboard(user):
    try:
        get_user = user_detail_model.query.filter_by(
            user_id=user["id"]).first()

        if not get_user:
            return jsonify({
                "msg": "No User Found",
                "status": 400,
            }), 400

        # Set User Detail
        user_detail = {
            "user_id": get_user.user_id,
            "user_first_name": get_user.user_first_name,
            "user_last_name": get_user.user_last_name,
            "user_email": get_user.user_email,
        }

        total_user = user_detail_model.query.count()  # Total user
        total_patients = patient_detail_model.query.count()  # Total Number Patient
        total_department = department_detail_model.query.count()  # Total Department

        # Total Number Patient (Male)
        total_male_patient = patient_detail_model.query.filter(
            patient_detail_model.patient_gender == "Male").count()

        # Total Number Patient (Female)
        total_female_patient = patient_detail_model.query.filter(
            patient_detail_model.patient_gender == "Female").count()

        # Total Number Patient Positive
        total_positive_patient = patient_detail_model.query \
            .join(feature_detail_model, patient_detail_model.patient_id == feature_detail_model.patient_id) \
            .filter(feature_detail_model.image_class == "Positive").count()

        # Total Number Patient Negative
        total_negative_patient = patient_detail_model.query \
            .join(feature_detail_model, patient_detail_model.patient_id == feature_detail_model.patient_id) \
            .filter(feature_detail_model.image_class == "Negative").count()

        # Total Number patient not diagnosed yet
        total_not_patient = patient_detail_model.query \
            .join(feature_detail_model, patient_detail_model.patient_id == feature_detail_model.patient_id) \
            .filter(feature_detail_model.image_class == "null").count()

        # Data Visualization (Positive)
        find_data_positive = feature_detail_model.query \
            .filter(feature_detail_model.image_class == "Positive") \
            .add_columns(feature_detail_model.feature_id, feature_detail_model.image_class, feature_detail_model.image_date_application) \
            .all()

        # Data Visualization (Negative)
        find_data_negative = feature_detail_model.query \
            .filter(feature_detail_model.image_class == "Negative") \
            .add_columns(feature_detail_model.feature_id, feature_detail_model.image_class, feature_detail_model.image_date_application) \
            .all()

        patient_count_by_month = defaultdict(
            lambda: {"positive": 0, "negative": 0})

        for record in find_data_positive:
            month = record.image_date_application.strftime("%Y-%m")
            patient_count_by_month[month]["positive"] += 1

        for record in find_data_negative:
            month = record.image_date_application.strftime("%Y-%m")
            patient_count_by_month[month]["negative"] += 1

        # Sort by bulan
        sorted_months = sorted(patient_count_by_month.items(
        ), key=lambda x: datetime.strptime(x[0], "%Y-%m"))

        patient_count_by_month_list = [
            {"month": datetime.strptime(month, "%Y-%m").strftime(
                "%b %Y"), "positive": counts["positive"], "negative": counts["negative"]}
            for month, counts in sorted_months
        ]

        return jsonify({
            "status": 200,
            "data": user_detail,
            "total_user": total_user,
            "total_patient": total_patients,
            "total_department": total_department,
            "total_not_patient": total_not_patient,
            "total_male_patient": total_male_patient,
            "total_female_patient": total_female_patient,
            "total_positive_patient": total_positive_patient,
            "total_negative_patient": total_negative_patient,
            "patient_count_by_month_list": patient_count_by_month_list
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
                        "zipcode": department.zipcode,
                        "district": department.district
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

            if user["doctorName"] == "" and user["doctor"] != "":
                get_user = user_detail_model.query \
                    .join(department_detail_model) \
                    .filter(department_detail_model.department_type_id == user["doctor"]) \
                    .all()

            elif user["doctorName"] != "" and user["doctor"] == "":
                search = "%{}%".format(user["doctorName"])
                get_user = user_detail_model.query \
                    .join(department_detail_model) \
                    .filter(user_detail_model.user_first_name.like(search)) \
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
            get_department = department_detail_model.query \
                .join(user_detail_model) \
                .filter(user_detail_model.user_id == department_detail_model.user_id) \
                .filter(user_detail_model.user_status == "Approved").all()

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
                    "zipcode": department.zipcode,
                    "district": department.district
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

            if department["departmentName"] == "" and department["department"] != "":
                get_department = department_detail_model.query \
                    .filter(department_detail_model.department_type_id == department["department"]) \
                    .all()

            elif department["departmentName"] != "" and department["department"] == "":
                search = "%{}%".format(department["departmentName"])
                get_department = department_detail_model.query \
                    .filter(department_detail_model.department_name.like(search)) \
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
                    "district": department.district,
                    "zipcode": department.zipcode
                }
                department_list.append(department_detail)

            return jsonify({
                "code": 200,
                "data": department_list,
                "search": search
            }), 200

    except Exception as e:
        return jsonify({
            "status": 500,
            "error": str(e),
        }), 500


# GET Doctor and department by Id
@admin.route('/admin/view/<int:id>', methods=['GET'])
@token_required_admin
def admin_view(user, id):
    try:
        user = user_detail_model.query.filter_by(
            user_id=id).first()  # Find Patient

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
            "user_profile_image": user.user_profile_image
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

        return jsonify({
            "msg": "User Found",
            "status": 200,
            "user": user_detail,
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


# POST Register User
@admin.route("/admin/register/user", methods=["POST"])
def register_user():
    try:
        data = request.get_json()  # get Post data from FrontEnd
        pwo = PasswordGenerator()
        pwo.minlen = 10
        pwo.maxlen = 20
        pwo.minuchars = 2
        pwo.minlchars = 3
        pwo.minnumbers = 1
        pwo.minschars = 1

        # Check if the email already exists or not
        existing_user = user_detail_model.query.filter_by(
            user_email=data['email']).first()
        if existing_user:
            return jsonify({
                "message": "The email is already registered.",
                "status": 400
            }), 400

        password = pwo.generate()
        encrypted_password = base64.b64encode(password.encode('utf-8'))

        # Create a new user
        new_user = user_detail_model(
            role_id=2,
            user_first_name=data['firstName'].upper(),
            user_last_name=data['lastName'].upper(),
            user_email=data['email'],
            user_password=encrypted_password,
            user_phone_number=data['phoneNumber'],
            user_status="Approved",
            user_date_application=datetime.today(),
        )

        db.session.add(new_user)
        db.session.commit()
        last_id = new_user.user_id  # Get the last inserted user ID

        # Create new department
        new_department = department_detail_model(
            department_type_id=data['departmentType'],
            user_id=last_id,
            department_name=data['departmentName'].upper(),
            department_address=data['departmentAddress'].upper(),
            city=data['departmentCity'].upper(),
            district=data['departmentDistrict'].upper(),
            state=data['departmentState'].upper(),
            zipcode=data['departmentZipCode'],
        )

        db.session.add(new_department)
        db.session.commit()

        msg = Message(
            'Welcome to Pneumocast - Your Registration Details',
            sender='muhdfauzan114@gmail.com',
            recipients=[data['email']]
        )
        msg.body = f'''Dear {data['firstName'].upper()} {data['lastName'].upper()},

        Welcome to Pneumocast Application! We are delighted to have you on board as a registered member of our platform. Your dedication to healthcare excellence is greatly appreciated, and we are thrilled to support you in your professional journey.

        Below are your registration details:
        Email: {data["email"]}
        Password: {password}

        We recommend that you keep this email in a safe place or securely manage your password for future reference. Please note that this password is case-sensitive.
        '''
        mail.send(msg)

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


# filter data visualisation
@admin.route("/admin/filter/visualizations/<int:id>", methods=["GET", "POST"])
def filter_visualization(id):
    try:
        if request.method == "POST":

            data = request.get_json()
            endDate = data["endDate"]
            image_class = data["class"]
            startDate = data["startDate"]

            convert_startDate = datetime.strptime(startDate, "%Y-%m")
            convert_endDate = datetime.strptime(endDate, "%Y-%m")

            find_data = department_detail_model.query \
                .filter(department_detail_model.user_id == id) \
                .join(patient_detail_model, department_detail_model.department_id == patient_detail_model.department_id) \
                .join(feature_detail_model, patient_detail_model.patient_id == feature_detail_model.patient_id) \
                .add_columns(feature_detail_model.feature_id, feature_detail_model.image_class, feature_detail_model.image_date_application, patient_detail_model.patient_name, patient_detail_model.patient_gender, patient_detail_model.patient_phone_number, feature_detail_model.lung_cancer) \
                .filter(feature_detail_model.image_date_application.between(convert_startDate, convert_endDate), feature_detail_model.image_class == image_class).all()

            monthly_patient = []
            for monthly in find_data:
                patient = {
                    "patient_name": monthly.patient_name,
                    "patient_gender": monthly.patient_gender,
                    "patient_phone_number": monthly.patient_phone_number,
                    "lung_cancer": monthly.lung_cancer,
                    "image_date_classification": monthly.image_date_application.strftime("%d %b, %Y"),
                    "image_date_application": monthly.image_date_application.strftime("%b %Y"),
                    "image_class": monthly.image_class,
                }
                monthly_patient.append(patient)

            patient_count_by_month = {}
            for entry in monthly_patient:
                month = entry["image_date_application"]
                if month in patient_count_by_month:
                    patient_count_by_month[month] += 1
                else:
                    patient_count_by_month[month] = 1

            months = list(patient_count_by_month.keys())
            counts = list(patient_count_by_month.values())

            return jsonify({
                "code": 200,
                "month": months,
                "patient_count": counts,
                "patient_list": monthly_patient
            })

        if request.method == "GET":
            find_data_positive = department_detail_model.query \
                .filter(department_detail_model.user_id == id) \
                .join(patient_detail_model, department_detail_model.department_id == patient_detail_model.department_id) \
                .join(feature_detail_model, patient_detail_model.patient_id == feature_detail_model.patient_id) \
                .add_columns(feature_detail_model.feature_id, feature_detail_model.image_class, feature_detail_model.image_date_application) \
                .filter(feature_detail_model.image_class == "Positive").all()

            find_data_negative = department_detail_model.query \
                .filter(department_detail_model.user_id == id) \
                .join(patient_detail_model, department_detail_model.department_id == patient_detail_model.department_id) \
                .join(feature_detail_model, patient_detail_model.patient_id == feature_detail_model.patient_id) \
                .add_columns(feature_detail_model.feature_id, feature_detail_model.image_class, feature_detail_model.image_date_application) \
                .filter(feature_detail_model.image_class == "Negative").all()

            patient_count_by_month = defaultdict(
                lambda: {"positive": 0, "negative": 0})

            for record in find_data_positive:
                month = record.image_date_application.strftime("%Y-%m")
                patient_count_by_month[month]["positive"] += 1

            for record in find_data_negative:
                month = record.image_date_application.strftime("%Y-%m")
                patient_count_by_month[month]["negative"] += 1

            # Sort by bulan
            sorted_months = sorted(patient_count_by_month.items(
            ), key=lambda x: datetime.strptime(x[0], "%Y-%m"))

            patient_count_by_month_list = [
                {"month": datetime.strptime(month, "%Y-%m").strftime(
                    "%b %Y"), "positive": counts["positive"], "negative": counts["negative"]}
                for month, counts in sorted_months
            ]

        return jsonify({
            "msg": "User Found",
            "status": 200,
            "patient_count_by_month": patient_count_by_month_list
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": 500,
            "error": str(e),
        }), 500
