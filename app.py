import os
import logging
from flask import Flask, session, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, logout_user
from sqlalchemy.orm import DeclarativeBase

# configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# initialize SQLAlchemy with our base
db = SQLAlchemy(model_class=Base)

# creating the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key_replace_in_production")

# force session to expire on app/browser close
app.config['SESSION_PERMANENT'] = False

# configure the SQLAlchemy database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///mental_health_tracker.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# initialize SQLAlchemy with the app
db.init_app(app)

# configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# import routes after app initialization to avoid circular imports
import routes

# create database tables within app context
with app.app_context():
    import model  # model.py
    db.create_all()

# force logout all users when the app starts (first request after boot)
@app.before_request
def force_logout_on_start():
    # run only once per app boot
    if not hasattr(app, 'has_reset_sessions'):
        app.has_reset_sessions = True

        # logout current user and clear session
        logout_user()
        session.clear()

        # clear 'remember_token' cookie by setting it to expire
        response = make_response(redirect(request.path))
        response.set_cookie('remember_token', '', expires=0)
        return response
