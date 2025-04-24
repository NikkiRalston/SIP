# initializes the Flask app, SQLAlchemy DB, and Flask-Login manager

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'routes.login'  # login view for @login_required

def create_app():
    app = Flask(__name__)
    
    # security key
    app.secret_key = os.environ.get("SESSION_SECRET", "dev_key_replace_in_production")

    # database config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///mental_health_tracker.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)

    # import and register routes
    from .routes import routes
    app.register_blueprint(routes)

    # creating tables on startup if needed
    with app.app_context():
        from . import models
        db.create_all()

    return app
