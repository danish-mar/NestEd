from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from app.config import Config
from app.extensions import db, bcrypt
from flask_migrate import Migrate


def create_app():
    """Factory function to create and configure the Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate = Migrate(app, db)  #  db migration assistant

    with app.app_context():
        # Import models before creating tables
        from app import models  # Ensure models are registered
        db.create_all()  # Create all tables if they don't exist

        # Register blueprints
        from app.routes import register_blueprints
        register_blueprints(app)

    return app
