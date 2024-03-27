from flask_sqlalchemy import SQLAlchemy
from models.departmentModel import department_detail_model
from models.adminModel import admin_Model
from db import db

class user_role_model(db.Model):
    __tablename__ = "user_role"

    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(255), unique=True)
    user_detail = db.relationship('user_detail_model', backref='user_detail', lazy='select')
    admin_detail = db.relationship(admin_Model, backref='admin_detail', lazy='select')

class user_detail_model(db.Model):
    __tablename__ ="user_detail"

    user_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('user_role.role_id'), nullable=False)
    user_first_name = db.Column(db.String(255), nullable=True)
    user_last_name = db.Column(db.String(255), nullable=True)
    user_email = db.Column(db.String(255), nullable=True, unique=True)
    user_password = db.Column(db.String(255), nullable=True)
    user_phone_number = db.Column(db.String(255), nullable=True)
    user_status = db.Column(db.String(20))
    department_detail = db.relationship(department_detail_model, backref='deparment_detail', lazy=False, uselist=False)
    


