from flask import Flask
from db import db

class admin_Model(db.Model):
    __tablename__ = "admin"

    admin_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('user_role.role_id'))
    admin_email = db.Column(db.String(255), nullable=False)
    admin_password = db.Column(db.String(255), nullable=False)