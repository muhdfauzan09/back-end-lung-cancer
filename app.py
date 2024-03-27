from flask import Flask, g
from flask_cors import CORS
from routes.auth import auth
from routes.admin import admin
from routes.user import user
from db import db

app = Flask(__name__)
app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(user)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/lung_cancer'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


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
