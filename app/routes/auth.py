from functools import wraps

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from flask import Blueprint, current_app, g, jsonify, request

from app.services.user_service import UserService

bp = Blueprint("auth", __name__, url_prefix="/api/auth")
user_service = UserService()


def _token_serializer():
    return URLSafeTimedSerializer(current_app.config["JWT_SECRET_KEY"])


def _token_max_age():
    return current_app.config["JWT_EXPIRATION_HOURS"] * 3600


def create_access_token(user):
    return _token_serializer().dumps(
        {"user_id": user.id, "username": user.username, "role": user.role.name}
    )


def _extract_token():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1].strip()
    return request.args.get("token")


def get_current_user():
    token = _extract_token()
    if not token:
        return None

    try:
        payload = _token_serializer().loads(token, max_age=_token_max_age())
    except (BadSignature, SignatureExpired):
        return None

    user = user_service.get(payload.get("user_id"))
    if not user:
        return None

    g.current_user = user
    return user


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_current_user():
            return jsonify({"error": "Autenticación requerida"}), 401
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"error": "Autenticación requerida"}), 401
        if user.role.name != "Admin":
            return jsonify({"error": "Acceso denegado. Requiere permisos de administrador."}), 403
        return f(*args, **kwargs)

    return decorated


@bp.route("/")
def root():
    return jsonify({"status": "ok", "message": "Auth API"})


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return jsonify({"status": "ok", "message": "Auth endpoint"})

    payload = request.get_json(silent=True) or request.form or {}
    username = payload.get("username")
    password = payload.get("password")

    if not username or not password:
        return jsonify({"error": "Usuario y contraseña son requeridos"}), 400

    user = user_service.find_by_username(username)
    if not user or not user.check_password(password):
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    token = create_access_token(user)
    return jsonify(
        {
            "token": token,
            "username": user.username,
            "role": user.role.name,
            "user_id": user.id,
        }
    )


@bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Sesión cerrada correctamente"})
