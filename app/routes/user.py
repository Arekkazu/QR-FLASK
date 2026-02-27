from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.routes.auth import login_required
from app.services.attendance_service import AttendanceService
from app.services.qr_service import QRService
from app.services.user_service import UserService

bp = Blueprint("user", __name__, url_prefix="/user")


def get_qr_service():
    """Obtener instancia de QRService con la configuración actual"""
    secret_key = current_app.config.get("QR_SECRET_KEY")
    if not secret_key:
        raise ValueError("QR_SECRET_KEY no está configurado")
    return QRService(secret_key)


@bp.route("/dashboard")
@login_required
def dashboard():
    """Dashboard del usuario con su código QR personal"""
    user_service = UserService()
    user = user_service.get(session.get("user_id"))

    if not user:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("auth.login"))

    # Generar código QR para el usuario
    qr_service = get_qr_service()
    qr_data = qr_service.create_qr_data(user.id)

    return render_template(
        "user/dashboard.html",
        title="Mi Dashboard",
        user=user,
        qr_token=qr_data["token"],
        qr_img=qr_data["image"],
        QR_EXPIRATION=current_app.config.get("QR_EXPIRATION", 60),
    )


@bp.route("/attendance")
@login_required
def attendance():
    """Historial de asistencias del usuario"""
    user_service = UserService()
    attendance_service = AttendanceService()

    user = user_service.get(session.get("user_id"))

    if not user:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("auth.login"))

    # Obtener historial de asistencias
    attendance_history = attendance_service.get_user_attendance(user.id)

    return render_template(
        "user/attendance.html",
        title="Mi Asistencia",
        user=user,
        attendance_history=attendance_history,
    )


@bp.route("/profile")
@login_required
def profile():
    """Perfil del usuario"""
    user_service = UserService()
    user = user_service.get(session.get("user_id"))

    if not user:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("auth.login"))

    return render_template("user/profile.html", title="Mi Perfil", user=user)


@bp.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    """Actualizar perfil del usuario"""
    user_service = UserService()
    user_id = session.get("user_id")

    username = request.form.get("username")
    password = request.form.get("password")

    try:
        kwargs = {"username": username}
        if password:
            kwargs["password"] = password

        user_service.update(user_id, **kwargs)
        flash("Perfil actualizado exitosamente", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except Exception as e:
        current_app.logger.error(f"Error al actualizar perfil: {e}")
        flash("Error al actualizar perfil. Intente nuevamente.", "danger")

    return redirect(url_for("user.profile"))
