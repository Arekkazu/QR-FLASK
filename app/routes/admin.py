from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    session,
)
from app.routes.auth import admin_required
from app.services.user_service import UserService
from app.services.attendance_service import AttendanceService
from app.services.qr_service import QRService

bp = Blueprint("admin", __name__, url_prefix="/admin")

# Inicializar servicios que no dependen de current_app
user_service = UserService()
attendance_service = AttendanceService()


def get_qr_service():
    """Obtener instancia de QRService con la configuración actual"""
    secret_key = current_app.config.get("QR_SECRET_KEY")
    if not secret_key:
        raise ValueError("QR_SECRET_KEY no está configurado")
    return QRService(secret_key)


@bp.route("/dashboard")
@admin_required
def dashboard():
    users = user_service.get_all()
    return render_template(
        "admin/dashboard.html", users=users, title="Panel de Administración"
    )


@bp.route("/scanner")
@admin_required
def scanner():
    return render_template("admin/scanner.html", title="Registrar Asistencia")


@bp.route("/record_attendance", methods=["POST"])
@admin_required
def record_attendance():
    qr_token = request.form["qr_token"]
    qr_service = get_qr_service()

    # Validar token con el servicio QR
    user_id = qr_service.validate_qr_data(qr_token)

    if not user_id:
        flash(
            "Token QR inválido o expirado. Por favor, solicita un nuevo código.",
            "danger",
        )
        return redirect(url_for("admin.scanner"))

    # Obtener usuario
    user = user_service.get(user_id)
    if not user:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("admin.scanner"))

    try:
        # Intentar registrar asistencia
        attendance = attendance_service.create(user_id)
        flash(f"✅ Asistencia registrada exitosamente para {user.username}!", "success")
    except ValueError as e:
        flash(str(e), "warning")
    except Exception as e:
        current_app.logger.error(f"Error al registrar asistencia: {e}")
        flash("Error al registrar asistencia. Intente nuevamente.", "danger")

    return redirect(url_for("admin.scanner"))


@bp.route("/add_user", methods=["POST"])
@admin_required
def add_user():
    username = request.form.get("username")
    password = request.form.get("password")
    role_name = request.form.get("role")

    if not all([username, password, role_name]):
        flash("Todos los campos son requeridos", "danger")
        return redirect(url_for("admin.dashboard"))

    try:
        # Crear usuario con el servicio
        user = user_service.create(username, password, role_name)
        flash(
            f'Usuario "{user.username}" creado exitosamente como {role_name}', "success"
        )
    except ValueError as e:
        flash(str(e), "danger")
    except Exception as e:
        current_app.logger.error(f"Error al crear usuario: {e}")
        flash("Error al crear usuario. Intente nuevamente.", "danger")

    return redirect(url_for("admin.dashboard"))


@bp.route("/edit_user", methods=["POST"])
@admin_required
def edit_user():
    user_id_str = request.form.get("user_id")
    username = request.form.get("username")
    password = request.form.get("password")
    role_name = request.form.get("role")

    if not user_id_str:
        flash("ID de usuario requerido", "danger")
        return redirect(url_for("admin.dashboard"))

    try:
        user_id = int(user_id_str)
        # Actualizar usuario con el servicio
        kwargs = {"username": username}
        if password:
            kwargs["password"] = password
        if role_name:
            kwargs["role_name"] = role_name

        updated_user = user_service.update(user_id, **kwargs)
        flash(f'Usuario "{updated_user.username}" actualizado exitosamente', "success")
    except ValueError as e:
        flash(str(e), "danger")
    except Exception as e:
        current_app.logger.error(f"Error al actualizar usuario: {e}")
        flash("Error al actualizar usuario. Intente nuevamente.", "danger")

    return redirect(url_for("admin.dashboard"))


@bp.route("/delete_user", methods=["POST"])
@admin_required
def delete_user():
    user_id_str = request.form.get("user_id")

    if not user_id_str:
        flash("ID de usuario requerido", "danger")
        return redirect(url_for("admin.dashboard"))

    try:
        user_id = int(user_id_str)
        # No permitir eliminar al usuario actual
        if user_id == session.get("user_id"):
            flash(
                "No puedes eliminar tu propia cuenta mientras estás conectado", "danger"
            )
            return redirect(url_for("admin.dashboard"))

        # Verificar si es el único admin
        if user_service.is_last_admin(user_id):
            flash("No puedes eliminar el único administrador del sistema", "danger")
            return redirect(url_for("admin.dashboard"))

        # Eliminar usuario
        user_service.delete(user_id)
        flash("Usuario eliminado permanentemente", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except Exception as e:
        current_app.logger.error(f"Error al eliminar usuario: {e}")
        flash("Error al eliminar usuario. Intente nuevamente.", "danger")

    return redirect(url_for("admin.dashboard"))
