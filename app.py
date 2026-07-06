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
    import application.controllers

def init_database():
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(role = "Admin").first()
        if not admin:
            admin = User(name = "Admin", email = "admin@gmail.com", password = "admin123", role = "Admin")
            db.session.add(admin)
            db.session.commit()

        trek_count = Trek.query.count()
        if trek_count == 0:
            staff = User(
                name="Vikas Singh",
                email="vikas@example.com",
                password="staff123",
                role="staff",
                contact="9876543210",
                approved=True,
            )
            user = User(
                name="Amit Sharma",
                email="amit@example.com",
                password="user123",
                role="user",
                contact="9123456780",
                approved=True,
            )
            db.session.add_all([staff, user])
            db.session.commit()

            profile = StaffProfile(user_id=staff.id, contact=staff.contact, status="Approved")
            db.session.add(profile)
            db.session.commit()

            trek1 = Trek(
                name="Everest Base Camp",
                location="Nepal",
                difficulty="Hard",
                duration=12,
                available_slots=10,
                assigned_staff_id=staff.id,
                status="Open",
                start_date="2026-05-20",
                end_date="2026-05-31",
                description="Simple trek description.",
                image="everestbasecamp.jpg",
            )
            trek2 = Trek(
                name="Roopkund Trek",
                location="Uttarakhand",
                difficulty="Moderate",
                duration=7,
                available_slots=8,
                assigned_staff_id=staff.id,
                status="Open",
                start_date="2026-04-10",
                end_date="2026-04-16",
                description="Simple trek description.",
                image="ropkundtrek.jpg",
            )
            trek3 = Trek(
                name="Kedarkantha Trek",
                location="Uttarakhand",
                difficulty="Easy",
                duration=5,
                available_slots=20,
                assigned_staff_id=staff.id,
                status="Closed",
                start_date="2026-05-10",
                end_date="2026-05-14",
                description="Simple trek description.",
                image="kedarkanthatrek.jpg",
            )
            trek4 = Trek(
                name="Hampta Pass",
                location="Himachal",
                difficulty="Moderate",
                duration=5,
                available_slots=12,
                status="Open",
                start_date="2026-03-18",
                end_date="2026-03-22",
                description="Simple trek description.",
                image="hamptapasstrek.jpg"
            )
            
            db.session.add_all([trek1, trek2, trek3, trek4])
            db.session.commit()

            old_booking = Booking(
                user_id=user.id,
                trek_id=trek2.id,
                booking_date="2026-04-01",
                status="Completed",
                payment_status="Paid",
            )
            db.session.add(old_booking)
            db.session.commit()



if __name__ == "__main__":
    init_database()
    app.run(debug=True)
