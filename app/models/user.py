from app import db
from app.models.base import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(BaseModel, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)

    # Relaciones
    role = db.relationship("Role", backref="users")
    attendances = db.relationship("Attendance", backref="user", lazy=True)

    def set_password(self, password: str) -> None:
        """Establecer la contraseña del usuario"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verificar la contraseña del usuario"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        """Representación serializable del modelo"""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role.name if self.role else None,
            "role_id": self.role_id,
        }

    def __repr__(self) -> str:
        return f"<User {self.username}>"
