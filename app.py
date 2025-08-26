from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import abort
from datetime import datetime
import re


app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY"  # replace with a strong random value

# Database setup (SQLite for demo; replace with MySQL/Postgres on AWS RDS)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        user = User.query.filter_by(username=session["username"]).first()
        if not user or not user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route("/")
def home():
    return render_template("home.html", user=session.get("username"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

# Password validation
        errors = []
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if not re.search(r"[A-Za-z]", password):
            errors.append("Password must include at least one letter.")
        if not re.search(r"[0-9]", password):
            errors.append("Password must include at least one number.")

        if errors:
            return render_template("register.html", errors=errors)

        hashed_pw = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["username"] = user.username
            return redirect(url_for("home"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/users")
def users_list():
    if "username" not in session:
        return redirect(url_for("login"))
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("users.html", users=users)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template("admin.html", users=users)

@app.route("/delete/<int:user_id>")
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == "admin":  # prevent deleting root admin
        return "Cannot delete main admin!"
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("admin_dashboard"))

@app.route("/make_admin/<int:user_id>")
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    return redirect(url_for("admin_dashboard"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # creates DB tables if not exist
        if not User.query.filter_by(username="yayu").first():
            admin = User(username="yayu", password=generate_password_hash("yayu031798", method="pbkdf2:sha256"), is_admin=True)
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
