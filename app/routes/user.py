from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session

from app.routes.auth import login_required
from app.services.attendance_service import AttendanceService
from app.services.qr_service import QRService
from app.services.user_service import UserService

bp = Blueprint("user", __name__, url_prefix="/user")

user_service = UserService()
attendance_service = AttendanceService()


def _qr_service():
    return QRService(current_app.config["QR_SECRET_KEY"])


@bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session.get("user_id")
    user = user_service.get(user_id)
    if not user:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("auth.login"))

    qr_data = _qr_service().create_qr_data(user.id)
    return render_template(
        "user/dashboard.html",
        user=user,
        qr_img=qr_data["image"],
        QR_EXPIRATION=current_app.config["QR_EXPIRATION"],
        title="Panel de Usuario",
    )


@bp.route("/attendance")
@login_required
def attendance():
    user_id = session.get("user_id")
    attendance_history = attendance_service.get_user_attendance(user_id)
    return render_template(
        "user/attendance.html",
        attendance_history=attendance_history,
        title="Mis Asistencias",
    )


@bp.route("/profile")
@login_required
def profile():
    user_id = session.get("user_id")
    user = user_service.get(user_id)
    if not user:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("auth.login"))

    return render_template("user/profile.html", user=user, title="Mi Perfil")


@bp.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    user_id = session.get("user_id")
    username = request.form.get("username")
    password = request.form.get("password")

    kwargs = {}
    if username:
        kwargs["username"] = username
    if password:
        kwargs["password"] = password

    try:
        updated_user = user_service.update(user_id, **kwargs)
        session["username"] = updated_user.username
        flash("Perfil actualizado exitosamente", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except Exception as e:
        current_app.logger.error(f"Error al actualizar perfil: {e}")
        flash("Error al actualizar perfil. Intente nuevamente.", "danger")

    return redirect(url_for("user.profile"))
