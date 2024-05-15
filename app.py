
import os
from db import db
from flask import Flask
from flask_cors import CORS
from routes.auth import auth
from routes.user import user
from routes.admin import admin
from dotenv import load_dotenv
from flask_mail import Mail, Message


app = Flask(__name__)
UPLOAD_URL_1 = 'static/images/classification'
UPLOAD_URL_2 = 'static/images/profiles'

app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(user)
load_dotenv()
CORS(app)


app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_SERVER'] = os.getenv('MAIL_SMTP')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['UPLOAD_URL_IMAGE_CLASS'] = UPLOAD_URL_1
app.config['UPLOAD_URL_IMAGE_PROFILE'] = UPLOAD_URL_2
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/lung_cancer'


db.init_app(app)
mail = Mail(app)


@app.teardown_appcontext
def close_db(error):
    db.session.remove()


# Create the database tables
def create_db():
    with app.app_context():
        db.create_all()


# Main driver function
if __name__ == '__main__':
    create_db()
    app.run(debug=True)
