from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique = True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20))
    approved= db.Column(db.Boolean, default=True)
    blacklisted=db.Column(db.Boolean, default=False)

    bookings = db.relationship('Booking', backref = 'user', lazy = True)
    assigned_treks = db.relationship('Trek', backref = 'user', lazy = True)

class StaffProfile(db.Model):
    __tablename__ = "staff_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    contact = db.Column(db.String(30))
    status = db.Column(db.String(30), default="Pending")

class Trek(db.Model):
    __tablename__ = "treks"
    
    id = db.Column(db.Integer, primary_key = True)
    trek_name = db.Column(db.String(100), nullable = False)
    location = db.Column(db.String(100), nullable = False)
    difficulty_level = db.Column(db.String(50), nullable = False)
    duration = db.Column(db.Integer, nullable = False)
    available_slots = db.Column(db.Integer, nullable = False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.String(30), default="open")
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    about = db.Column(db.Text)

    bookings = db.relationship('Booking', backref = 'Trek', lazy = True)

class Booking(db.Model):
    __name__ = "bookings"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    booking_date = db.Column(db.String(20), nullable = False)
    status = db.Column(db.String(50), default = "Booked")
    payment_status = db.Column(db.String(30), default = "Paid")
    





