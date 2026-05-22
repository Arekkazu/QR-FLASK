from datetime import datetime, timezone, timedelta
from functools import wraps

import jwt
from flask import Blueprint, request, jsonify, current_app

from app.services.user_service import UserService

bp = Blueprint("auth", __name__, url_prefix="/api/auth")
user_service = UserService()


def _make_token(user):
    cfg = current_app.config
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.name,
        "exp": datetime.now(timezone.utc) + timedelta(hours=cfg["JWT_EXPIRATION_HOURS"]),
    }
    return jwt.encode(payload, cfg["JWT_SECRET_KEY"], algorithm="HS256")


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token requerido"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
        request.current_user = payload
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token requerido"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
        if payload.get("role") != "Admin":
            return jsonify({"error": "Acceso denegado"}), 403
        request.current_user = payload
        return f(*args, **kwargs)
    return decorated


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400

    user = user_service.find_by_username(username)
    if not user or not user.check_password(password):
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    return jsonify({
        "token": _make_token(user),
        "username": user.username,
        "role": user.role.name,
    })


@bp.route("/me", methods=["GET"])
@jwt_required
def me():
    return jsonify(request.current_user)
