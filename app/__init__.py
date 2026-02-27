import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name=None):
    app = Flask(__name__)

    # Determinar configuración
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")

    # Cargar configuración desde el diccionario
    app.config.from_object(config[config_name])

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # type: ignore

    # Configurar user loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User

        return User.query.get(int(user_id))

    # Registro de blueprints
    from app.routes import blueprints

    for bp in blueprints:
        app.register_blueprint(bp)

    # Context processor para funciones de utilidad
    @app.context_processor
    def utility_processor():
        from datetime import datetime

        return dict(now=datetime.now())

    # Ruta raíz que redirige al login
    @app.route("/")
    def index():
        from flask import redirect, url_for

        return redirect(url_for("auth.login"))

    # Crear tablas y datos iniciales al inicializar la aplicación
    with app.app_context():
        initialize_database()

    return app


def initialize_database():
    """Inicializar la base de datos con datos por defecto"""
    from app import db
    from app.models.role import Role
    from app.models.user import User

    db.create_all()

    # Crear roles por defecto
    if not Role.query.filter_by(name="Admin").first():
        admin_role = Role(name="Admin")
        user_role = Role(name="User")
        db.session.add(admin_role)
        db.session.add(user_role)
        db.session.commit()
        print("Roles por defecto creados")

    # Crear usuario admin por defecto
    if not User.query.filter_by(username="admin").first():
        admin_role = Role.query.filter_by(name="Admin").first()
        if admin_role:
            admin = User(username="admin", role_id=admin_role.id)
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("Usuario admin creado: admin / admin123")

    # Crear usuario de ejemplo
    if not User.query.filter_by(username="usuario").first():
        user_role = Role.query.filter_by(name="User").first()
        if user_role:
            user = User(username="usuario", role_id=user_role.id)
            user.set_password("usuario123")
            db.session.add(user)
            db.session.commit()
            print("Usuario de ejemplo creado: usuario / usuario123")
