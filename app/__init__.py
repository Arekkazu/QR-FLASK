import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from config import config

db = SQLAlchemy()


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")

    app.config.from_object(config[config_name])

    db.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"])

    from app.routes import blueprints
    for bp in blueprints:
        app.register_blueprint(bp)

    with app.app_context():
        _initialize_database()

    return app


def _initialize_database():
    from app.models.role import Role
    from app.models.user import User

    db.create_all()

    if not Role.query.filter_by(name="Admin").first():
        db.session.add(Role(name="Admin"))
        db.session.add(Role(name="User"))
        db.session.commit()

    if not User.query.filter_by(username="admin").first():
        admin_role = Role.query.filter_by(name="Admin").first()
        admin = User(username="admin", role_id=admin_role.id)
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()

    if not User.query.filter_by(username="usuario").first():
        user_role = Role.query.filter_by(name="User").first()
        user = User(username="usuario", role_id=user_role.id)
        user.set_password("usuario123")
        db.session.add(user)
        db.session.commit()
