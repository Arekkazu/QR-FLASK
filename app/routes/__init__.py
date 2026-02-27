# Importar blueprints para registrarlos en la app
from .auth import bp as auth_bp
from .admin import bp as admin_bp
from .user import bp as user_bp

# Lista de blueprints para registrar
blueprints = [auth_bp, admin_bp, user_bp]
