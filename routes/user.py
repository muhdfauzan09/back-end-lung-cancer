from flask import Blueprint, jsonify, request
from routes.authenticateUser import token_required_user
from models.userModel import user_detail_model
from models.patientModel import patient_detail_model, feature_detail_model
from models.departmentModel import department_detail_model
from datetime import date
from db import db
import pickle

user = Blueprint("user", __name__)
UPLOAD_URL = '/path/to/the/upload'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}


# GET Dashboard
@user.route('/user/dashboard', methods=['GET'])
@token_required_user
def get_dashboard(user):
    try:
        get_user = user_detail_model.query.filter_by(
            user_id=user["user_id"]).first()
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
            # "model": loaded_model_predictions.tolist(),
        }), 200

    except Exception as e:
        return jsonify({
            "status": 500,
            "error": str(e)
        }), 500


# GET Visualisation
@user.route("/user/get/visualisation", methods=["GET"])
@token_required_user
def get_visualisation(user):
    return jsonify({
        "user": user["user_id"]
    })


# GET Patient List
@user.route("/user/get/patient", methods=["GET"])
@token_required_user
def get_patient(user):
    try:
        get_patient = patient_detail_model.query.filter_by(
            department_id=user["department_id"]).all()

        if not get_patient:
            return jsonify({
                "status": 500,
                "msg": "User Not Found",
            }), 500

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
            "code": 200,
            "data": patient_list
        })

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str(e)
        })


# GET Patient Details
@user.route("/user/get/patient/details/<int:id>", methods=['GET'])
@token_required_user
def get_patient_details(user, id):
    try:
        get_patient = patient_detail_model.query.filter_by(patient_id=id).first()
        
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
            patient_name=data["fullName"],
            patient_gender=data["gender"],
            patient_phone_number=data["phoneNumber"],
            patient_address1=data["address1"],
            patient_address2=data["address2"],
            patient_postcode=data['postcode']
        )

        db.session.add(new_patient)
        db.session.commit()
        patient_id = new_patient.patient_id  # Get the last inserted user ID

        new_feature = feature_detail_model(
            patient_id=patient_id,
            date_application=date.today(),
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


@user.route("/user/post/prediction/image", methods=["POST"])
def post_prediction_image():
    if 'file' not in request.files:
        return jsonify({
            "msg" : "File Not Found",
        })
    
    file = request.files['file']

    return jsonify({
        "status" : 200,
        "file" : file.filename
    }), 200