from flask import Flask, render_template, request, redirect, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import google.genai as genai
from google.genai import types

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mhm_secret_key")

# Gemini AI setup
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
gemini_client = None
if GEMINI_API_KEY:
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        gemini_client = None

SYSTEM_PROMPT = (
    "You are MHM Assistant, a caring and knowledgeable menstrual health assistant "
    "for the Care For Her platform. Only answer questions related to menstrual health, "
    "hygiene, reproductive health, nutrition, mental wellness during periods, "
    "cycle tracking, and women's health. "
    "Keep answers concise, warm, and easy to understand. "
    "If a question is unrelated to women's or menstrual health, politely decline."
)

# PostgreSQL Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://postgres:root@localhost:5433/careforher")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Disable browser caching
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# ================= DATABASE MODELS =================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(200))

    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))

    height = db.Column(db.Float)
    weight = db.Column(db.Float)

    cycle_length = db.Column(db.Integer)


class Cycle(db.Model):
    __tablename__ = "period_track_history"

    id = db.Column(db.Integer, primary_key=True)

    user_name = db.Column(db.String(100))

    last_period = db.Column(db.String(20))
    cycle_length = db.Column(db.Integer)
    next_period = db.Column(db.String(20))


# Create database tables
with app.app_context():
    db.create_all()
    inspector = inspect(db.engine)
    columns = [column["name"] for column in inspector.get_columns(User.__tablename__)]

    if "phone" not in columns:
        db.session.execute(
            text(f"ALTER TABLE {User.__tablename__} ADD COLUMN phone VARCHAR(20)")
        )
        db.session.commit()

# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/emergency")
def emergency():

    if "user" not in session:
        return redirect("/login")

    return render_template("emergency.html")


@app.route("/quiz")
def quiz():

    if "user" not in session:
        return redirect("/login")

    return render_template("quiz.html")


@app.route("/chatbot", methods=["POST"])
def chatbot():

    data = request.get_json()
    msg = data.get("message", "").strip()

    if not msg:
        return jsonify({"reply": "Please type a message."})

    if not gemini_client:
        return jsonify({"reply": "AI assistant is not configured yet. Please add the GEMINI_API_KEY."})

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=msg,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )
        reply = response.text
    except Exception as e:
        print("Gemini error:", e)
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            reply = "⏳ The AI is temporarily unavailable due to rate limits. Please try again in a minute."
        else:
            reply = "Sorry, I couldn't process that. Please try again."

    return jsonify({"reply": reply})


# ================= PROFILE =================

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user" not in session:
        return redirect("/login")

    user = User.query.filter_by(name=session["user"]).first()

    if not user:
        session.pop("user", None)
        return redirect("/login")

    if request.method == "POST":

        user.name = request.form.get("name")
        user.email = request.form.get("email")
        user.phone = request.form.get("phone") or user.phone

        age = request.form.get("age")
        height = request.form.get("height")
        weight = request.form.get("weight")
        cycle_length = request.form.get("cycle_length")

        user.age = int(age) if age else None
        user.height = float(height) if height else None
        user.weight = float(weight) if weight else None
        user.cycle_length = int(cycle_length) if cycle_length else None

        session["user"] = user.name

        # Handle password change
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if current_password and new_password:
            if not check_password_hash(user.password, current_password):
                flash("❌ Current password is incorrect.", "danger")
                return redirect("/profile")
            if new_password != confirm_password:
                flash("❌ New passwords do not match.", "danger")
                return redirect("/profile")
            user.password = generate_password_hash(new_password)

        db.session.commit()

        flash("✅ Profile updated successfully!", "success")

        return redirect("/profile")

    return render_template("profile.html", user=user)


# ================= REGISTER =================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        age = request.form.get("age")
        gender = request.form.get("gender")
        height = request.form.get("height")
        weight = request.form.get("weight")
        cycle_length = request.form.get("cycle_length")

        phone = request.form.get("phone")

        existing_email = User.query.filter_by(email=email).first()
        existing_phone = User.query.filter_by(phone=phone).first()

        if existing_email:
            flash(
                "Email already registered. Please login or use a different email.",
                "danger",
            )
            return render_template("register.html")

        if existing_phone:
            flash(
                "Mobile number already in use. Please login or use a different number.",
                "danger",
            )
            return render_template("register.html")

        user = User(
            name=name,
            email=email,
            phone=phone,
            password=password,
            age=int(age) if age else None,
            gender=gender,
            height=float(height) if height else None,
            weight=float(weight) if weight else None,
            cycle_length=int(cycle_length) if cycle_length else None,
        )

        db.session.add(user)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash("An account with that email or phone already exists.", "danger")
            return render_template("register.html")

        flash(
            "✅ User created successfully! Please login with your credentials.",
            "success",
        )

        return render_template("register.html")

    return render_template("register.html")


# ================= LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None
    no_user = False

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user"] = user.name

            flash("✅ Login successful!", "success")

            return redirect("/dashboard")

        elif not user:
            no_user = True

        else:
            error = "Wrong password. Please try again."

    return render_template("login.html", error=error, no_user=no_user)


# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    user = User.query.filter_by(name=session["user"]).first()

    if not user:
        session.pop("user", None)
        return redirect("/login")

    cycle = (
        Cycle.query.filter_by(user_name=user.name)
        .order_by(Cycle.id.desc())
        .first()
    )

    last_period = cycle.last_period if cycle else None
    next_period = cycle.next_period if cycle else None
    cycle_length = cycle.cycle_length if cycle else 28

    history = (
        Cycle.query.filter_by(user_name=user.name)
        .order_by(Cycle.id.desc())
        .all()
    )

    return render_template(
        "dashboard.html",
        name=user.name,
        last_period=last_period,
        next_period=next_period,
        cycle_length=cycle_length,
        history=history,
    )


# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.pop("user", None)
    return redirect("/")


# ================= CYCLE TRACKER =================

@app.route("/tracker", methods=["GET", "POST"])
def tracker():

    if "user" not in session:
        return redirect("/login")

    prediction = None

    user = User.query.filter_by(name=session["user"]).first()

    if not user:
        session.pop("user", None)
        return redirect("/login")

    if request.method == "POST":

        last_period = request.form["last_period"]

        form_cycle = request.form.get("cycle_length")
        cycle_length = int(form_cycle) if form_cycle else (user.cycle_length if user.cycle_length else 28)

        last_date = datetime.strptime(last_period, "%Y-%m-%d")

        next_date = last_date + timedelta(days=cycle_length)

        prediction = next_date.strftime("%Y-%m-%d")

        cycle = Cycle(
            user_name=user.name,
            last_period=last_period,
            cycle_length=cycle_length,
            next_period=prediction,
        )

        db.session.add(cycle)
        db.session.commit()

    return render_template("tracker.html", prediction=prediction)


# ================= MACHINE LOCATOR =================

@app.route("/locator")
def locator():

    if "user" not in session:
        return redirect("/login")

    return render_template("locator.html", maps_api_key=os.environ.get("MAPS_API_KEY", ""))


# ================= EDUCATION =================

@app.route("/education")
def education():

    if "user" not in session:
        return redirect("/login")

    return render_template("education.html")


# ================= RUN APP =================

if __name__ == "__main__":
    app.run(debug=True)