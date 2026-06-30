from datetime import date
from application.models import db, User, StaffProfile, Trek, Booking
from flask import current_app as app
from flask import redirect, request, render_template, session

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
        db.commit()

        if role == "staff":
            profile = StaffProfile(user_id=new_user.id, contact=contact, status ="Pending")
            db.session.add(profile)
            db.commit()

        return redirect("/login")
    
    return render_template("register.html")


        



