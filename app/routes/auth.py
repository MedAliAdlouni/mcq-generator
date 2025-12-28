from flask import Blueprint, request, jsonify, render_template, url_for, redirect, flash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

from ..db import LocalSession
from ..models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")

# Flask-login initialization
login_manager = LoginManager()
login_manager.login_view = "auth.login"

# Function to load user
@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login user loader callback.

    Flask-Login only stores the authenticated user's ID in the session cookie.
    Whenever it needs the actual User object (e.g., to populate `current_user`
    or to check `@login_required`), it calls this function with that ID.

    By registering this function with the `@login_manager.user_loader`
    decorator, we tell Flask-Login how to retrieve a user from our database:
    look up the User whose primary key matches `user_id` and return it.
    If this function is missing, users will not stay logged in across requests.
    """
    session = LocalSession()
    user = session.get(User, user_id)
    session.close()
    return user

# registration page
@bp.route("/register", methods=["GET", "POST"])
def register():
    # If the user is already looged in
    if current_user.is_authenticated:
        return redirect(url_for("ui.home"))
    
    # If method is POST (process the submitted form)
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            flash("All fields are required", "error")
            return redirect(url_for("auth.register"))
        
        # Check whether account already exists
        session = LocalSession()
        existing = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing:
            flash("This account already exists", "error")
            session.close()
            return redirect(url_for("auth.register"))
        
        user = User(username=username, email=email)
        # important to save the hashed password
        user.set_password(password) 
        session.add(user)
        session.commit()
        session.close()

        flash("Successful registration! You can now login")
        return redirect(url_for("auth.login"))
    
    return render_template("register.html")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("ui.home"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        session = LocalSession()
        user = session.query(User).filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Incorrect IDs", "error")
            session.close()
            return redirect(url_for("auth.login"))
        
        login_user(user)
        session.close()
        flash("Welcome {user.username}")
        return redirect(url_for("ui.home"))
    return render_template("login.html")
    
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for("auth.login"))