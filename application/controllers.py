from datetime import date
from application.models import db, User, StaffProfile, Trek, Booking
from flask import current_app as app
from flask import redirect, request, render_template, session
import os
from werkzeug.utils import secure_filename

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email, password=password).first()
        if user and not user.blacklisted:
            if user.role == "staff" and not user.approved:
                return redirect("/login")
            
            session["user_id"]=user.id
            session["name"]=user.name
            session["role"]=user.role

            if user.role == "Admin":
                return redirect("/admin")
            elif user.role == "staff":
                return redirect("/staff")
            elif user.role == "user":
                return redirect("/user")
        
        return redirect("/login")
    
    return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        contact = request.form.get("contact")
        role = request.form.get("role")

        if role not in ["user","staff"]:
            return redirect("/register")
        old_user = User.query.filter_by(email=email).first()
        if old_user:
            return redirect("/register")
        
        approved_status = True
        if role == "staff":
            approved_status = False

        new_user = User(
            name = name,
            email = email,
            password = password,
            contact = contact,
            role = role,
            approved = approved_status,
        )
        db.session.add(new_user)
        db.session.commit()

        if role == "staff":
            profile = StaffProfile(user_id=new_user.id, contact=contact, status ="Pending")
            db.session.add(profile)
            db.session.commit()

        return redirect("/login")
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "Admin":
        return redirect ("/login")
    
    metrics = {
        "treks":Trek.query.count(),
        "users":User.query.filter_by(role="user").count(),
        "staff":User.query.filter_by(role="staff").count(),
        "bookings":Booking.query.count(),
    }

    recent_bookings = Booking.query.order_by(Booking.id.desc()).limit(5).all()
    booking_rows=[]
    for booking in recent_bookings:
        user = User.query.get(booking.user_id)
        trek = Trek.query.get(booking.trek_id)
        booking_rows.append({
            "id":booking.id,
            "user_name":user.name,
            "trek_name":trek.name,
            "booking_date":booking.booking_date,
            "status":booking.status,
        })
    return render_template("admin_dashboard.html", totals=metrics, bookings=booking_rows)


@app.route("/admin/treks")
def admin_treks():
    if session.get("role") != "Admin":
        return redirect("/login")
    
    search_text=request.args.get("q","")
    if search_text:
        treks = Trek.query.filter(
            (Trek.name.like("%" + search_text + "%")) |
            (Trek.location.like("%" + search_text + "%"))
            
        ).all()
    else:
        treks=Trek.query.all()

    trek_rows=[]
    for trek in treks:
        staff_name = "-"
        if trek.assigned_staff_id:
            staff = User.query.get(trek.assigned_staff_id)
            if staff:
                staff_name=staff.name
        trek_rows.append({
            "id":trek.id,
            "name":trek.name,
            "location":trek.location,
            "difficulty":trek.difficulty,
            "available_slots":trek.available_slots,
            "staff_name":staff_name,
            "status": trek.status
        })
    
    return render_template("admin_treks.html", q=search_text, treks=trek_rows)

@app.route("/admin/treks/add", methods=["GET","POST"])
def add_trek():
    if session.get("role") != "Admin":
        return redirect("/login")

    if request.method=="POST":
        image = request.files.get("image")

        filename = None

        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        trek = Trek(
            name = request.form.get("name"),
            location=request.form.get("location"),
            difficulty=request.form.get("difficulty"),
            duration=request.form.get("duration"),
            available_slots=request.form.get("available_slots"),
            assigned_staff_id = request.form.get("assigned_staff_id"),
            status = request.form.get("status"),
            start_date=request.form.get("start_date"),
            end_date=request.form.get("end_date"),
            description=request.form.get("description"),
            image=filename,
        )
        db.session.add(trek)
        db.session.commit()
        return redirect("/admin/treks")
    staff = User.query.filter_by(role="staff", approved = True, blacklisted = False).all()
    return render_template("trek_form.html", staff=staff, trek=None)

@app.route("/admin/treks/<int:trek_id>/edit", methods=["GET", "POST"])
def edit_trek(trek_id):
    if session.get("role") != "Admin":
        return redirect("/login")
    trek=Trek.query.get_or_404(trek_id)

    if request.method == "POST":
        trek.name=request.form.get("name")
        trek.location=request.form.get("location")
        trek.difficulty=request.form.get("difficulty")
        trek.duration=request.form.get("duration")
        trek.available_slots=request.form.get("available_slots")
        trek.assigned_staff_id=request.form.get("assigned_staff_id") or None
        trek.status=request.form.get("status")
        trek.start_date=request.form.get("start_date")
        trek.end_date=request.form.get("end_date")
        trek.description=request.form.get("description")
        image = request.files.get("image")

        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            trek.image = filename
        
        db.session.commit()
        return redirect("/admin/treks")
    staff=User.query.filter_by(role="staff", approved=True, blacklisted=False).all()
    return render_template("trek_form.html", staff=staff, trek=trek)

@app.route("/admin/treks/<int:trek_id>/delete")
def delete_trek(trek_id):
    if session.get("role") != "Admin":
        return redirect("/login")
    
    trek=Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    return redirect("/admin/treks")

@app.route("/admin/staff")
def admin_staff():
    if session.get("role") != "Admin":
        return redirect("/login")

    staff=User.query.filter_by(role="staff").all()
    return render_template("admin_staff.html", staff=staff)

@app.route("/admin/staff/<int:user_id>/<action>")
def staff_action(user_id, action):
    if session.get("role") != "Admin":
        return redirect("/login")
    
    staff=User.query.get_or_404(user_id)

    if action=="approve":
        staff.approved=True
        staff.blacklisted=False
        profile = StaffProfile.query.filter_by(user_id=staff.id).first()
        if profile:
            profile.status = "Approved"
    elif action=="blacklist":
        staff.blacklisted=True
        profile=StaffProfile.query.filter_by(user_id=staff.id).first()
        if profile:
            profile.status="Blacklisted"
    elif action=="remove":
        db.session.delete(staff)

    db.session.commit()
    return redirect("/admin/staff")

@app.route("/admin/users")
def admin_users():
    if session.get("role") != "Admin":
        return redirect("/login")
    
    search_text = request.args.get("q", "")
    if search_text:
        users=User.query.filter(
            (User.role=="user") &
            ((User.name.like("%" + search_text +"%")) | (User.email.like("%" + search_text + "%")))
        ).all()
    else:
        users=User.query.filter_by(role="user").all()
    
    return render_template("admin_users.html", users=users, q=search_text)

@app.route("/admin/users/<int:user_id>/blacklist")
def blacklist_user(user_id):
    if session.get("role") != "Admin":
        return redirect("/login")
    
    user=User.query.get_or_404(user_id)
    user.blacklisted = not user.blacklisted
    db.session.commit()
    return redirect("/admin/users")

@app.route("/admin/bookings")
def admin_bookings():
    if session.get("role") != "Admin":
        return redirect("/login")
    bookings = Booking.query.order_by(Booking.id.desc()).all()
    booking_rows = []
    for booking in bookings:
        user = User.query.get(booking.user_id)
        trek = Trek.query.get(booking.trek_id)
        booking_rows.append({
            "id": booking.id,
            "user_name":user.name,
            "trek_name":trek.name,
            "booking_date":booking.booking_date,
            "status":booking.status,
            "payment_status":booking.payment_status,
        })
    return render_template("admin_bookings.html", bookings=booking_rows)

@app.route("/staff")
def staff_dashboard():
    if session.get("role") != "staff":
        return redirect("/login")
    
    treks = Trek.query.filter_by(assigned_staff_id=session.get("user_id")).all()
    trek_rows =[]
    for trek in treks:
        count=Booking.query.filter_by(trek_id=trek.id,status="Booked").count()
        trek_rows.append({
            "id":trek.id,
            "name":trek.name,
            "location":trek.location,
            "participant_count":count,
            "available_slots":trek.available_slots,
            "status":trek.status,
        })

    return render_template("staff_dashboard.html", treks=trek_rows)

@app.route("/staff/trek/<int:trek_id>",methods=["GET","POST"])
def staff_trek(trek_id):
    if session.get("role") != "staff":
        return redirect("/login")
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != session.get("user_id"):
        return redirect("/staff")
    
    if request.method == "POST":
        trek.available_slots = request.form.get("available_slots")
        trek.status = request.form.get("status")
        
        if trek.status == "Completed":
            bookings=Booking.query.filter_by(trek_id=trek.id, status="Booked").all()
            for booking in bookings:
                booking.status="Completed"
        
        db.session.commit()
        return redirect("staff/trek/" + str(trek.id))
    
    participant_rows = []
    bookings = Booking.query.filter_by(trek_id=trek.id).all()
    for booking in bookings:
        user = User.query.get(booking.user_id)
        participant_rows.append({
            "user_name":user.name,
            "email":user.email,
            "booking_date":booking.booking_date,
            "status":booking.status,
        })
    return render_template("staff_trek.html", trek=trek, participants=participant_rows)

@app.route("/user")
def user_dashboard():
    if session.get("role") != "user":
        return redirect("/login")
    
    difficulty = request.args.get("difficulty", "")
    location = request.args.get("location","")

    trek_query = Trek.query.filter_by(status="Open")
    if difficulty:
        trek_query = trek_query.filter_by(difficulty=difficulty)
    if location:
        trek_query = trek_query.filter(Trek.location.like("%" + location +  "%"))
    
    treks=trek_query.all()

    bookings=Booking.query.filter_by(user_id=session.get("user_id")).order_by(Booking.id.desc()).all()
    booking_rows = []
    for booking in bookings:
        trek = Trek.query.get(booking.trek_id)
        booking_rows.append({
            "id": booking.id,
            "trek_name": trek.name,
            "booking_date": booking.booking_date,
            "status": booking.status,
        })

    return render_template("user_dashboard.html", treks=treks, bookings=booking_rows, difficulty=difficulty, location=location)

@app.route("/trek/<int:trek_id>")
def trek_detail(trek_id):
    if session.get("role") != "user":
        return redirect("/login")
    trek=Trek.query.get_or_404(trek_id)
    return render_template("trek_detail.html", trek=trek)

@app.route("/book/<int:trek_id>")
def book_trek(trek_id):
    if session.get("role") != "user":
        return redirect("/login")
    trek = Trek.query.get_or_404(trek_id)

    old_booking = Booking.query.filter_by(user_id=session.get("user_id"), trek_id=trek.id).first()
    booked_count = Booking.query.filter_by(trek_id=trek.id, status="Booked").count()

    if old_booking:
        return redirect("/user")
    
    if trek.status != "Open":
        return redirect("/user")
    
    if booked_count >= trek.available_slots:
        return redirect("/user")
    
    booking=Booking(
        user_id=session.get("user_id"),
        trek_id=trek.id,
        booking_date=str(date.today()),
        status="Booked",
        payment_status="Paid",
    )
    db.session.add(booking)
    db.session.commit()
    return redirect("/user")

@app.route("/bookings")
def my_bookings():
    if session.get("role") != "user":
        return redirect("/login")
    
    bookings = Booking.query.filter_by(user_id=session.get("user_id")).order_by(Booking.id.desc()).all()
    booking_rows = []
    for booking in bookings:
        trek = Trek.query.get(booking.trek_id)
        booking_rows.append({
            "id": booking.id,
            "trek_name": trek.name,
            "booking_date": booking.booking_date,
            "start_date": trek.start_date,
            "end_date": trek.end_date,
            "status": booking.status,
        })

    return render_template("my_bookings.html", bookings=booking_rows)

@app.route("/booking/<int:booking_id>/cancel")
def cancel_booking(booking_id):
    if session.get("role") != "user":
        return redirect("/login")
    
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id == session.get("user_id") and booking.status == "Booked":
        booking.status = "Cancelled"
        db.session.commit()
    
    return redirect("/bookings")

@app.route("/history")
def history():
    if session.get("role") != "user":
        return redirect("/login")
    
    bookings=Booking.query.filter_by(user_id=session.get("user_id")).all()
    history_rows = []
    for booking in bookings:
        if booking.status in ["Completed","Cancelled"]:
            trek = Trek.query.get(booking.trek_id)
            history_rows.append({
                "trek_name":trek.name,
                "start_date":trek.start_date,
                "end_date":trek.end_date,
                "status":booking.status,
            })
    return render_template("history.html", bookings=history_rows)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not session.get("user_id"):
        return redirect("/login")
    
    user=User.query.get_or_404(session.get("user_id"))

    if request.method == "POST":
        user.name = request.form.get("name")
        user.contact=request.form.get("contact")
        session["name"]=user.name
        db.session.commit()
        return redirect("/profile")
    
    return render_template("profile.html", user=user)

        







        



