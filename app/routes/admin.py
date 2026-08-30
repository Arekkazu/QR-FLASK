from flask import Blueprint, request, jsonify, current_app, session

from app.routes.auth import admin_required, jwt_required
from app.services.attendance_service import AttendanceService
from app.services.qr_service import QRService
from app.services.user_service import UserService

bp = Blueprint("admin", __name__, url_prefix="/api/admin")
user_service = UserService()
attendance_service = AttendanceService()


def _qr_service():
    return QRService(current_app.config["QR_SECRET_KEY"])


@bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    users = user_service.get_all()
    return jsonify([
        {"id": u.id, "username": u.username, "role": u.role.name}
        for u in users
    ])


@bp.route("/record_attendance", methods=["POST"])
@admin_required
def record_attendance():
    data = request.get_json(silent=True) or {}
    qr_token = data.get("qr_token", "")
    if not qr_token:
        return jsonify({"error": "qr_token requerido"}), 400

    user_id = _qr_service().validate_qr_data(qr_token)
    if not user_id:
        return jsonify({"error": "Token QR inválido o expirado"}), 400

    user = user_service.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    try:
        attendance = attendance_service.create(user_id)
        return jsonify({
            "message": f"Asistencia registrada para {user.username}",
            "attendance_id": attendance.id,
            "timestamp": attendance.timestamp.isoformat(),
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 409


@bp.route("/users", methods=["POST"])
@admin_required
def add_user():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    role_name = data.get("role", "")

    if not all([username, password, role_name]):
        return jsonify({"error": "username, password y role son requeridos"}), 400

    try:
        user = user_service.create(username, password, role_name)
        return jsonify({"id": user.id, "username": user.username, "role": role_name}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409


@bp.route("/users/<int:user_id>", methods=["PUT"])
@admin_required
def edit_user(user_id):
    data = request.get_json(silent=True) or {}
    kwargs = {}
    if data.get("username"):
        kwargs["username"] = data["username"]
    if data.get("password"):
        kwargs["password"] = data["password"]
    if data.get("role"):
        kwargs["role_name"] = data["role"]
    try:
        user = user_service.update(user_id, **kwargs)
        return jsonify({"id": user.id, "username": user.username})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    caller_id = int(request.current_user["sub"])
    if user_id == caller_id:
        return jsonify({"error": "No puedes eliminar tu propia cuenta"}), 400
    if user_service.is_last_admin(user_id):
        return jsonify({"error": "No puedes eliminar el único administrador"}), 400
    try:
        user_service.delete(user_id)
        return jsonify({"message": "Usuario eliminado"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@bp.route("/attendance_logs", methods=["GET"])
@admin_required
def get_attendance_logs():
    attendances = attendance_service.get_all()
    # Sort by timestamp descending so the newest are at the top
    attendances.sort(key=lambda x: x.timestamp, reverse=True)
    return jsonify([
        {
            "id": a.id,
            "username": a.user.username if a.user else "Desconocido",
            "role": a.user.role.name if a.user and a.user.role else "Desconocido",
            "date": a.date.isoformat() if a.date else None,
            "timestamp": a.timestamp.isoformat() if a.timestamp else None
        }
        for a in attendances
    ])
