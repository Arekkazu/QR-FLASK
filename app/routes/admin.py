from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
)

from app.routes.auth import admin_required
from app.services.attendance_service import AttendanceService
from app.services.qr_service import QRService
from app.services.user_service import UserService

bp = Blueprint("admin", __name__, url_prefix="/api/admin")
user_service = UserService()
attendance_service = AttendanceService()


def _qr_service():
    return QRService(current_app.config["QR_SECRET_KEY"])


@bp.route("/dashboard")
@admin_required
def dashboard():
    users = user_service.get_all()
    return jsonify([user.to_dict() for user in users])


@bp.route("/scanner")
@admin_required
def scanner():
    try:
        recent_attendances = attendance_service.get_recent(10)
    except Exception:
        recent_attendances = []
    results = []
    for attendance in recent_attendances:
        try:
            user = user_service.get(attendance.user_id)
        except Exception:
            user = None

        results.append(
            {
                "attendance": attendance.to_dict(),
                "user": user.to_dict() if user else None,
            }
        )

    return jsonify(results)


@bp.route("/record_attendance", methods=["POST"])
@admin_required
def record_attendance():
    payload = request.get_json(silent=True) or request.form or {}
    qr_token = payload.get("qr_token")

    if not qr_token:
        return jsonify({"error": "qr_token es requerido"}), 400

    user_id = _qr_service().validate_qr_data(qr_token)
    if not user_id:
        return jsonify(
            {"error": "Token QR inválido o expirado. Por favor, solicita un nuevo código."}
        ), 400

    user = user_service.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    try:
        attendance = attendance_service.create(user_id)
        return jsonify(
            {
                "message": f"Asistencia registrada exitosamente para {user.username}",
                "attendance": attendance.to_dict(),
                "user": user.to_dict(),
            }
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error al registrar asistencia: {e}")
        return jsonify({"error": "Error al registrar asistencia. Intente nuevamente."}), 500


@bp.route("/users", methods=["POST"])
@admin_required
def add_user():
    payload = request.get_json(silent=True) or request.form or {}
    username = payload.get("username")
    password = payload.get("password")
    role_name = payload.get("role")

    if not all([username, password, role_name]):
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    try:
        user = user_service.create(username, password, role_name)
        return jsonify({"message": "Usuario creado exitosamente", "user": user.to_dict()})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error al crear usuario: {e}")
        return jsonify({"error": "Error al crear usuario. Intente nuevamente."}), 500


@bp.route("/users/<int:user_id>", methods=["PUT"])
@admin_required
def edit_user(user_id):
    payload = request.get_json(silent=True) or request.form or {}
    username = payload.get("username")
    password = payload.get("password")
    role_name = payload.get("role") or payload.get("role_name")

    try:
        kwargs = {"username": username}
        if password:
            kwargs["password"] = password
        if role_name:
            kwargs["role_name"] = role_name

        updated_user = user_service.update(user_id, **kwargs)
        return jsonify({"message": "Usuario actualizado exitosamente", "user": updated_user.to_dict()})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error al actualizar usuario: {e}")
        return jsonify({"error": "Error al actualizar usuario. Intente nuevamente."}), 500


@bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    from app.routes.auth import get_current_user

    try:
        current_user = get_current_user()
        if current_user and user_id == current_user.id:
            return jsonify({"error": "No puedes eliminar tu propia cuenta mientras estás conectado"}), 400

        if user_service.is_last_admin(user_id):
            return jsonify({"error": "No puedes eliminar el único administrador del sistema"}), 400

        user_service.delete(user_id)
        return jsonify({"message": "Usuario eliminado permanentemente"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error al eliminar usuario: {e}")
        return jsonify({"error": "Error al eliminar usuario. Intente nuevamente."}), 500
