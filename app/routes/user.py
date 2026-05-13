from flask import Blueprint, request, jsonify, current_app

from app.routes.auth import jwt_required
from app.services.attendance_service import AttendanceService
from app.services.qr_service import QRService
from app.services.user_service import UserService

bp = Blueprint("user", __name__, url_prefix="/api/user")


def _qr_service():
    return QRService(current_app.config["QR_SECRET_KEY"])


@bp.route("/dashboard", methods=["GET"])
@jwt_required
def dashboard():
    user_id = request.current_user["sub"]
    user = UserService().get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    qr_data = _qr_service().create_qr_data(user.id)
    return jsonify({
        "username": user.username,
        "role": user.role.name,
        "qr_token": qr_data["token"],
        "qr_img": qr_data["image"],
        "qr_expiration": current_app.config["QR_EXPIRATION"],
    })


@bp.route("/attendance", methods=["GET"])
@jwt_required
def attendance():
    user_id = request.current_user["sub"]
    records = AttendanceService().get_user_attendance(user_id)
    return jsonify([
        {"id": r.id, "timestamp": r.timestamp.isoformat()}
        for r in records
    ])


@bp.route("/profile", methods=["GET"])
@jwt_required
def profile():
    user = UserService().get(request.current_user["sub"])
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify({"id": user.id, "username": user.username, "role": user.role.name})


@bp.route("/profile", methods=["PUT"])
@jwt_required
def update_profile():
    data = request.get_json(silent=True) or {}
    user_id = request.current_user["sub"]
    kwargs = {}
    if data.get("username"):
        kwargs["username"] = data["username"]
    if data.get("password"):
        kwargs["password"] = data["password"]
    try:
        UserService().update(user_id, **kwargs)
        return jsonify({"message": "Perfil actualizado"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
