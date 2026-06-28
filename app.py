from flask import Flask
from application.models import db, User, StaffProfile, Trek, Booking
import os
app = Flask(__name__)
app.secret_key = "simple secret key"

database_path = os.path.join(os.path.dirname(__file__), "trekking.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + database_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return "Welcome to my Trekking App!"

if __name__ == "__main__":
    app.run(debug=True)
