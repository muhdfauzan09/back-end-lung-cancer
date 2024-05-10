from flask_sqlalchemy import SQLAlchemy
from db import db


class patient_detail_model(db.Model):
    __tablename__ = "patient_detail"

    patient_id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey(
        'department_detail.department_id'), nullable=False)
    patient_name = db.Column(db.String(255), nullable=True)
    patient_gender = db.Column(db.String(255), nullable=True)
    patient_address1 = db.Column(db.String(255), nullable=True)
    patient_address2 = db.Column(db.String(255), nullable=True)
    patient_postcode = db.Column(db.String(255), nullable=True)
    patient_phone_number = db.Column(db.String(255), nullable=True)
    feature_detail = db.relationship(
        "feature_detail_model", backref='feature', lazy='select')


class feature_detail_model(db.Model):
    __tablename__ = "feature_detail"

    feature_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey(
        'patient_detail.patient_id'), nullable=False)
    date_application = db.Column(db.Date, nullable=True)
    smoking = db.Column(db.Integer, nullable=True)
    yellow_fingers = db.Column(db.Integer, nullable=True)
    anxiety = db.Column(db.Integer, nullable=True)
    peer_pressure = db.Column(db.Integer, nullable=True)
    chronic_disease = db.Column(db.Integer, nullable=True)
    fatigue = db.Column(db.Integer, nullable=True)
    allergy = db.Column(db.Integer, nullable=True)
    wheezing = db.Column(db.Integer, nullable=True)
    alcohol_consuming = db.Column(db.Integer, nullable=True)
    coughing = db.Column(db.Integer, nullable=True)
    shortness_breath = db.Column(db.Integer, nullable=True)
    swallowing_difficulty = db.Column(db.Integer, nullable=True)
    chest_pain = db.Column(db.Integer, nullable=True)
    lung_cancer = db.Column(db.Integer, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    image_class = db.Column(db.String(255), nullable=True)
