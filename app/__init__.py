from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from app.config import Config
from app.extensions import db, bcrypt
from app.models import HOD  # Import HOD model

def create_app():
    """Factory function to create and configure the Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate = Migrate(app, db)  # db migration assistant

    with app.app_context():
        from app import models  # Ensure models are registered
        db.create_all()  # Create all tables if they don't exist

        # Check if there is an HOD, otherwise create a default admin HOD
        if not HOD.query.first():
            default_hod = HOD(
                name="Admin",
                email="admin@mit.edu",
                phone="9999999999",
            )
            default_hod.set_password("admin123")  # Set default password
            db.session.add(default_hod)
            db.session.commit()
            print("✅ Default HOD created: Email: admin@college.edu, Password: admin123")

        # Register blueprints
        from app.routes import register_blueprints
        register_blueprints(app)

    return app
