from flask import Flask, g
from flask_cors import CORS
from routes.auth import auth
from routes.admin import admin
from routes.user import user
from db import db

app = Flask(__name__)

UPLOAD_URL_1 = 'static/images/classification'
UPLOAD_URL_2 = 'static/images/profiles'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(user)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/lung_cancer'
app.config['UPLOAD_URL_IMAGE_CLASS'] = UPLOAD_URL_1
app.config['UPLOAD_URL_IMAGE_PROFILE'] = UPLOAD_URL_2

db.init_app(app)


@app.route('/test', )
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
