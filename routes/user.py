import os
import base64
import pickle
import numpy as np

from db import db
from datetime import datetime
from flask_mail import Mail, Message
from keras.preprocessing import image
from werkzeug.utils import secure_filename
from password_generator import PasswordGenerator
from routes.authenticateUser import token_required_user
from flask import Blueprint, jsonify, request, current_app

# Models
from models.userModel import user_detail_model
from models.departmentModel import department_detail_model
from models.patientModel import patient_detail_model, feature_detail_model


user = Blueprint("user", __name__)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
mail = Mail()


# Check the file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# GET Dashboard
@user.route('/user/get/dashboard', methods=['GET'])
@token_required_user
def get_dashboard(user):
    try:
        user_details = user_detail_model.query \
            .join(department_detail_model) \
            .filter(department_detail_model.user_id == user["user_id"]).first()

        if not user_details:
            return jsonify({
                "msg": "User not found",
                "status": 400,
            }), 400

        department = user_details.department_detail  # Relationship Table

        # Total Number Patient
        total_patients = patient_detail_model.query \
            .filter(patient_detail_model.department_id == department.department_id).count()

        # Male Patient Count
        male_patient_count = patient_detail_model.query \
            .filter(patient_detail_model.department_id == department.department_id) \
            .filter(patient_detail_model.patient_gender == "Male").count()

        # Female patient Count
        female_patient_count = patient_detail_model.query \
            .filter(patient_detail_model.department_id == department.department_id) \
            .filter(patient_detail_model.patient_gender == "Female").count()

        # Postive Patient Count
        postive_patient_count = patient_detail_model.query \
            .join(feature_detail_model) \
            .filter(patient_detail_model.department_id == department.department_id) \
            .filter(feature_detail_model.lung_cancer == "1").count()

        # Negative Patient Count
        negative_patient_count = patient_detail_model.query \
            .join(feature_detail_model) \
            .filter(patient_detail_model.department_id == department.department_id) \
            .filter(feature_detail_model.lung_cancer == "0").count()

        # Get top 10 Patient
        get_patient = patient_detail_model.query \
            .filter(patient_detail_model.department_id == department.department_id) \
            .order_by(patient_detail_model.patient_id.desc()).limit(10).all()

        patient_list = []
        for patient in get_patient:
            patient_detail = {
                "patient_id": patient.patient_id,
                "patient_name": patient.patient_name,
                "department_id": patient.department_id,
                "patient_gender": patient.patient_gender,
                "patient_address1": patient.patient_address1,
                "patient_address2": patient.patient_address2,
                "patient_postcode": patient.patient_postcode,
                "patient_phone_number": patient.patient_phone_number,
            }

            if patient.feature_detail:
                for feature in patient.feature_detail:
                    feature_detail = {
                        "lung_cancer": feature.lung_cancer,
                        "date_consultation": feature.date_application
                    }
                patient_detail.update(feature_detail)

            patient_list.append(patient_detail)

        return jsonify({
            "status": 200,
            "patient_list": patient_list,
            "total_patients": total_patients,
            "user_data": user_details.user_email,
            "male_patient_count": male_patient_count,
            "female_patient_count": female_patient_count,
            "positive_patient_count": postive_patient_count,
            "negative_patient_count": negative_patient_count,
            "user_image_profile": user_details.user_profile_image
        }), 200

    except Exception as e:
        return jsonify({
            "status": 500,
            "error": str(e)
        }), 500


# GET Setting
@user.route("/user/get/setting", methods=["GET"])
@token_required_user
def get_setting(user):
    try:
        get_user = user_detail_model.query.filter_by(
            user_id=user["user_id"]).first()

        if not get_user:
            return jsonify({
                "status": 404,
                "msg": "User not found"
            }), 404

        user_detail = {
            "user_first_name": get_user.user_first_name,
            "user_last_name": get_user.user_last_name,
            "user_email": get_user.user_email,
            "user_phone_number": get_user.user_phone_number,
            "user_status": get_user.user_status,
            "user_profile_image": get_user.user_profile_image
        }

        department = get_user.department_detail  # Relationship
        department_detail = {
            "department_type_id": department.department_type_id,
            "department_name": department.department_name,
            "department_address": department.department_address,
            "city": department.city,
            "zipCode": department.zipcode,
            "state": department.state,
        }

        return jsonify({
            "status": 200,
            "user_detail": user_detail,
            "department_detail": department_detail,
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": "An error occurred while processing the request",
            "error": str(e)
        }), 500


# POST Update Password
@user.route("/user/post/new_password", methods=["POST"])
@token_required_user
def change_password(user):
    try:
        get_data = request.get_json()
        check_user = user_detail_model.query.filter_by(
            user_id=user['user_id']).first()

        if not check_user:
            return jsonify({
                "code": 400,
                "msg": "No user found"
            }), 400

        get_password = check_user.user_password
        decode_password = base64.b64decode(get_password).decode("utf-8")

        if decode_password == get_data['oldPassword']:
            encode_password = base64.b64encode(
                get_data["newPassword"].encode("utf-8"))

            # Update and Commit
            check_user.user_password = encode_password
            db.session.commit()

            msg = Message(
                'Pneumocast - Password Updated',
                sender='muhdfauzan114@gmail.com',
                recipients=[check_user.user_email],
            )
            msg.body = f'''Dear {check_user.user_first_name} {check_user.user_last_name},

            Your password for accessing Pneumocast has been successfully updated. We want to ensure the security of your account, so please keep this information confidential and do not share it with anyone.

            Thank you for choosing Pneumocast for your healthcare needs.

            Best regards,
            The Pneumocast Team
            '''
            mail.send(msg)

            return jsonify({
                "code": 200,
                "msg": "Password has been updated"
            }), 200
        else:
            return jsonify({
                "code": 400,
                "msg": "Old password is not correct."
            }), 400

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": "An error occurred while processing the request",
            "error": str(e)
        }), 500


# POST Upload Image Profile
@user.route("/user/post/add_user_profile", methods=["POST"])
@token_required_user
def add_user_profile(user):
    try:
        if 'file' not in request.files:
            return jsonify({
                "msg": "No file part in the request"
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                "msg": "No selected file"
            }), 400

        if file and allowed_file(file.filename):
            upload_directory = current_app.config['UPLOAD_URL_IMAGE_PROFILE']
            if not os.path.exists(upload_directory):
                os.makedirs(upload_directory)

            check_user = user_detail_model.query.filter_by(
                user_id=user['user_id']).first()  # Check User

            file_name = secure_filename(file.filename)
            image_url = os.path.join(upload_directory, file_name)
            file.save(image_url)  # Save File
            check_user.user_profile_image = image_url  # Update Column
            db.session.commit()
            return jsonify({
                "msg": "File uploaded successfully"
            }), 200

        else:
            return jsonify({
                "msg": "File type not allowed"
            }), 400

    except Exception as e:
        return jsonify({
            "msg": "Error processing the image: " + str(e)
        }), 500


# POST Edit Image Profile
@user.route("/user/post/edit_user_profile", methods=["POST"])
@token_required_user
def edit_user_profile(user):
    try:
        if 'file' not in request.files:
            return jsonify({
                "msg": "No file part in the request"
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                "msg": "No selected file"
            }), 400

        if file and allowed_file(file.filename):
            upload_directory = current_app.config['UPLOAD_URL_IMAGE_PROFILE']
            if not os.path.exists(upload_directory):
                os.makedirs(upload_directory)

            check_user = user_detail_model.query.filter_by(
                user_id=user['user_id']).first()  # Check User

            file_name = secure_filename(file.filename)
            image_url = os.path.join(upload_directory, file_name)

            # Check if the image is already exists
            if check_user.user_profile_image is None:
                file.save(image_url)
            elif os.path.exists(check_user.user_profile_image):
                os.remove(check_user.user_profile_image)
                file.save(image_url)

            check_user.user_profile_image = image_url
            db.session.commit()

            return jsonify({
                "code": 200,
                "msg": "File uploaded successfully"
            }), 200

        else:
            return jsonify({
                "code": 404,
                "msg": "File type not allowed"
            }), 400

    except Exception as e:
        return jsonify({
            "msg": "Error processing the image: " + str(e)
        }), 500


# GET Visualisation
@user.route("/user/get/visualisation", methods=["GET"])
@token_required_user
def get_visualisation(user):
    return jsonify({
        "user": user["user_id"]
    })


# POST find patient / GET Patient List
@user.route("/user/get/patient", methods=["GET", "POST"])
@token_required_user
def get_patient(user):
    try:
        if request.method == "GET":
            patients = patient_detail_model.query \
                .filter_by(department_id=user["department_id"]) \
                .order_by(patient_detail_model.patient_id.desc()).all()

            if not patients:
                return jsonify({
                    "code": 404,
                    "msg": "No patients found for the given department",
                }), 404

            patient_list = []
            for patient in patients:
                patient_detail = {
                    "patient_id": patient.patient_id,
                    "patient_name": patient.patient_name,
                    "department_id": patient.department_id,
                    "patient_gender": patient.patient_gender,
                    "patient_address1": patient.patient_address1,
                    "patient_address2": patient.patient_address2,
                    "patient_postcode": patient.patient_postcode,
                    "patient_phone_number": patient.patient_phone_number,
                }

                if patient.feature_detail:
                    for feature in patient.feature_detail:
                        feature_detail = {
                            "lung_cancer": feature.lung_cancer,
                            "image_class": feature.image_class,
                        }
                    patient_detail.update(feature_detail)

                patient_list.append(patient_detail)

            return jsonify({
                "code": 200,
                "data": patient_list
            })

        elif request.method == "POST":
            lung_cancer = request.get_json()

            if "patient" not in lung_cancer or "lung_cancer" not in lung_cancer:
                return jsonify({
                    "code": 400,
                    "msg": "Patient name or lung cancer status not provided"
                }), 400

            if lung_cancer["patient"] is "" and lung_cancer["lung_cancer"] is not "":
                patients = patient_detail_model.query \
                    .join(feature_detail_model) \
                    .filter(patient_detail_model.department_id == user["department_id"]) \
                    .filter(feature_detail_model.lung_cancer == lung_cancer["lung_cancer"]) \
                    .all()

            elif lung_cancer["patient"] is not "" and lung_cancer["lung_cancer"] is "":
                search = "%{}%".format(lung_cancer["patient"])
                patients = patient_detail_model.query \
                    .join(feature_detail_model) \
                    .filter(patient_detail_model.department_id == user["department_id"]) \
                    .filter(patient_detail_model.patient_name.like(search)) \
                    .all()

            else:
                search = "%{}%".format(lung_cancer["patient"])
                patients = patient_detail_model.query \
                    .join(feature_detail_model) \
                    .filter(patient_detail_model.department_id == user["department_id"]) \
                    .filter(patient_detail_model.patient_name.like(search)) \
                    .filter(feature_detail_model.lung_cancer == int(lung_cancer["lung_cancer"])) \
                    .all()

            patient_data = []
            for patient in patients:
                patient_detail = {
                    "patient_id": patient.patient_id,
                    "patient_name": patient.patient_name,
                    "department_id": patient.department_id,
                    "patient_gender": patient.patient_gender,
                    "patient_address1": patient.patient_address1,
                    "patient_address2": patient.patient_address2,
                    "patient_postcode": patient.patient_postcode,
                    "patient_phone_number": patient.patient_phone_number,
                }

                if patient.feature_detail:
                    for feature in patient.feature_detail:
                        feature_detail = {
                            "lung_cancer": feature.lung_cancer,
                            "image_class": feature.image_class
                        }
                    patient_detail.update(feature_detail)

                patient_data.append(patient_detail)

            return jsonify({
                "code": 200,
                "data": patient_data
            })

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": "An error occurred while processing the request",
            "error": str(e)
        }), 500


# GET Patient Details
@user.route("/user/get/patient/details/<int:id>", methods=['GET'])
@token_required_user
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
                    "image_path": feature.image_path,
                    "image_class": feature.image_class,
                    "lung_cancer": feature.lung_cancer,
                    "image_date_application": feature.image_date_application
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


# GET Prediction
@user.route("/user/get/prediction", methods=["GET"])
@token_required_user
def get_prediction(user):
    return jsonify({
        "user": user["user_id"]
    })


# POST Prediction
@user.route("/user/post/prediction", methods=["POST"])
@token_required_user
def post_prediction(user):
    try:
        department = department_detail_model.query.filter_by(
            user_id=user["user_id"]).first()
        data = request.get_json()  # Get data

        # Load the model
        loaded_model = pickle.load(
            open(r"C:\programming\Learning\lung-cancer-model.pkl", "rb"))
        feature_input = [[1, int(data["smoking"]), int(data['yellow_fingers']), int(data['anxiety']), int(data['peer_pressure']), int(data['chronic_disease']),
                          int(data['fatigue']), int(data['allergy']), int(data['wheezing']), int(
                              data["alcohol_consuming"]), int(data["coughing"]), int(data["shortness_breath"]),
                          int(data["swallowing_difficulty"]), int(data["chest_pain"])]]

        loaded_model_predictions = loaded_model.predict(feature_input)

        new_patient = patient_detail_model(
            department_id=department.department_id,
            patient_name=data["fullName"].upper(),
            patient_gender=data["gender"],
            patient_phone_number=data["phoneNumber"],
            patient_address1=data["address1"].upper(),
            patient_address2=data["address2"].upper(),
            patient_postcode=data['postcode'].upper()
        )

        db.session.add(new_patient)
        db.session.commit()
        patient_id = new_patient.patient_id  # Get the last inserted user ID

        new_feature = feature_detail_model(
            patient_id=patient_id,
            date_application=datetime.today(),
            smoking=data["smoking"],
            yellow_fingers=data['yellow_fingers'],
            anxiety=data['anxiety'],
            peer_pressure=data['peer_pressure'],
            chronic_disease=data['chronic_disease'],
            fatigue=data['fatigue'],
            allergy=data['allergy'],
            wheezing=data['wheezing'],
            alcohol_consuming=data["alcohol_consuming"],
            coughing=data["coughing"],
            shortness_breath=data["shortness_breath"],
            swallowing_difficulty=data["swallowing_difficulty"],
            chest_pain=data["chest_pain"],
            lung_cancer=loaded_model_predictions.tolist()
        )

        db.session.add(new_feature)
        db.session.commit()

        return jsonify({
            "code": 200,
            "result": loaded_model_predictions.tolist()
        }), 200

    except Exception as e:
        return jsonify({
            "status": 500,
            "error": str(e)
        }), 500


# POST Image Classificaton
@user.route("/user/post/prediction/image/<int:patient_id>", methods=["POST"])
def post_prediction_image(patient_id):
    if request.method == "POST":
        try:
            # Check if the image from is sent to the server
            if 'file' not in request.files:
                return jsonify({
                    "msg": "File Not Found"
                }), 400

            file = request.files['file']

            if file.filename == '':
                return jsonify({
                    "msg": "No selected file"
                }), 400

            if file and allowed_file(file.filename):
                upload_directory = current_app.config['UPLOAD_URL_IMAGE_CLASS']
                if not os.path.exists(upload_directory):
                    os.makedirs(upload_directory)

                # Check data
                check_update = feature_detail_model.query.filter_by(
                    patient_id=patient_id).first()

                file_name = secure_filename(file.filename)
                image_url = os.path.join(upload_directory, file_name)

                # Check if the image is already exists
                if check_update.image_path is None:
                    file.save(image_url)
                elif os.path.exists(check_update.image_path):
                    os.remove(check_update.image_path)
                    file.save(image_url)

                # Loaded the model
                loaded_model = pickle.load(
                    open(r"C:\Sem 5\FYP\lung-cancer-image-classification.pkl", "rb"))

                image_pred = image.load_img(image_url, target_size=(224, 224))
                image_pred = image.img_to_array(image_pred)
                image_pred = np.expand_dims(image_pred, axis=0)

                predictions = loaded_model.predict(image_pred)
                if predictions[0][0] == 1.0:
                    prediction_result = "Negative"
                elif predictions[0][1] == 1.0:
                    prediction_result = "Positive"

                # Update data
                check_update.image_path = image_url
                check_update.image_class = prediction_result
                check_update.image_date_application = datetime.now()
                db.session.commit()

                return jsonify({
                    "status": 200,
                    "file": image_url,
                    "prediction": prediction_result
                }), 200
            else:
                return jsonify({
                    "msg": "File is not supported",
                    "error": 400
                }), 400

        except Exception as e:
            return jsonify({
                "msg": "Error processing the image: " + str(e)
            }), 500
