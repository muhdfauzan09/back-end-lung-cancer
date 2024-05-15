from flask_sqlalchemy import SQLAlchemy
from models.patientModel import patient_detail_model
from db import db


class department_type_model(db.Model):
    __tablename__ = "department_type"
    department_type_id = db.Column(db.Integer, primary_key=True)
    department_type_name = db.Column(db.String(10))
    deparment = db.relationship(
        'department_detail_model', backref='deparment', lazy='select')


class department_detail_model(db.Model):
    __tablename__ = "department_detail"
    department_id = db.Column(db.Integer, primary_key=True)
    department_type_id = db.Column(db.Integer, db.ForeignKey(
        'department_type.department_type_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user_detail.user_id'), nullable=False)
    department_name = db.Column(db.String(255), nullable=True)
    department_address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    district = db.Column(db.String(255), nullable=True)
    state = db.Column(db.String(255), nullable=True)
    zipcode = db.Column(db.String(255))
    patient = db.relationship(patient_detail_model,
                              backref='patient', lazy='select')
