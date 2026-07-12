from flask import Flask
from application.models import db, User, StaffProfile, Trek, Booking
import os
app = Flask(__name__)
app.secret_key = "simple secret key"

app.config["UPLOAD_FOLDER"] = os.path.join("static", "images")

database_path = os.path.join(os.path.dirname(__file__), "trekking.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + database_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    import application.controllers

def init_database():
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(role = "Admin").first()
        if not admin:
            admin = User(name = "Admin", email = "admin@gmail.com", password = "admin123", role = "Admin")
            db.session.add(admin)
            db.session.commit()

        


if __name__ == "__main__":
    init_database()
    app.run(debug=True)
