from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.services.user_service import UserService

bp = Blueprint("auth", __name__, url_prefix="/auth")

# Inicializar servicio
user_service = UserService()


@bp.route("/")
def root():
    """Redirigir a la página de login"""
    return redirect(url_for("auth.login"))


# Decoradores de autenticación
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Por favor, inicia sesión para acceder", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Por favor, inicia sesión para acceder", "warning")
            return redirect(url_for("auth.login"))

        user = user_service.get(session["user_id"])
        if not user or user.role.name != "Admin":
            flash("Acceso denegado. Requiere permisos de administrador.", "danger")
            return redirect(url_for("user.dashboard"))
        return f(*args, **kwargs)

    return decorated_function


@bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(
            url_for(
                "admin.dashboard"
                if session.get("role") == "Admin"
                else "user.dashboard"
            )
        )

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = user_service.find_by_username(username)

        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role.name

            flash(f"¡Bienvenido, {user.username}!", "success")
            return redirect(
                url_for(
                    "admin.dashboard" if user.role.name == "Admin" else "user.dashboard"
                )
            )

        flash("Usuario o contraseña incorrectos", "danger")

    return render_template("login.html", title="Iniciar Sesión")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente", "success")
    return redirect(url_for("auth.login"))
