from flask import Blueprint, jsonify, request, current_app

from app.routes.auth import login_required, get_current_user
from app.services.attendance_service import AttendanceService
from app.services.qr_service import QRService
from app.services.user_service import UserService

bp = Blueprint("user", __name__, url_prefix="/api/user")

user_service = UserService()
attendance_service = AttendanceService()


def _qr_service():
    return QRService(current_app.config["QR_SECRET_KEY"])


@bp.route("/dashboard")
@login_required
def dashboard():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    qr_data = _qr_service().create_qr_data(user.id)
    return jsonify(
        {
            "user": user.to_dict(),
            "qr_token": qr_data["token"],
            "qr_img": qr_data["image"],
            "qr_expiration": current_app.config["QR_EXPIRATION"],
        }
    )


@bp.route("/attendance")
@login_required
def attendance():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    attendance_history = attendance_service.get_user_attendance(user.id)
    return jsonify([attendance.to_dict() for attendance in attendance_history])


@bp.route("/profile")
@login_required
def profile():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify(user.to_dict())


@bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    payload = request.get_json(silent=True) or request.form or {}
    username = payload.get("username")
    password = payload.get("password")

    kwargs = {}
    if username:
        kwargs["username"] = username
    if password:
        kwargs["password"] = password

    try:
        updated_user = user_service.update(user.id, **kwargs)
        return jsonify({"message": "Perfil actualizado exitosamente", "user": updated_user.to_dict()})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error al actualizar perfil: {e}")
        return jsonify({"error": "Error al actualizar perfil. Intente nuevamente."}), 500
