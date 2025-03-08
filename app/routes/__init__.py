from app.routes.frontend_routes import frontend_blueprint
from app.routes.hod_routes import hod_blueprint
from app.routes.teacher_routes import teacher_blueprint


def register_blueprints(app):
    app.register_blueprint(frontend_blueprint, url_prefix="/")
    app.register_blueprint(hod_blueprint, url_prefix="/api/hod")
    app.register_blueprint(teacher_blueprint, url_prefix="/api/teacher")
