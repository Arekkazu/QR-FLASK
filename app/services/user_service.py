from app.models.role import Role
from app.models.user import User
from app.services.base_service import BaseService


class UserService(BaseService):
    def create(self, username: str, password: str, role_name: str) -> User:
        """Crear un nuevo usuario"""
        if User.query.filter_by(username=username).first():
            raise ValueError(f"El usuario '{username}' ya existe")

        role = Role.query.filter_by(name=role_name).first()
        if not role:
            raise ValueError(f"El rol '{role_name}' no existe")

        user = User(username=username, role_id=role.id)
        user.set_password(password)

        from app import db

        db.session.add(user)
        db.session.commit()

        return user

    def get(self, user_id: int) -> User | None:
        """Obtener un usuario por ID"""
        return User.query.get(user_id)

    def get_all(self) -> list[User]:
        """Obtener todos los usuarios"""
        return User.query.all()

    def update(self, user_id: int, **kwargs) -> User:
        """Actualizar un usuario existente"""
        user = self.get(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        if "username" in kwargs:
            username = kwargs["username"]
            existing_user = User.query.filter(
                User.username == username, User.id != user_id
            ).first()
            if existing_user:
                raise ValueError(f"El nombre de usuario '{username}' ya está en uso")
            user.username = username

        if "password" in kwargs:
            user.set_password(kwargs["password"])

        if "role_name" in kwargs:
            role_name = kwargs["role_name"]
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                raise ValueError(f"El rol '{role_name}' no existe")
            user.role_id = role.id

        from app import db

        db.session.commit()
        return user

    def delete(self, user_id: int) -> None:
        """Eliminar un usuario"""
        user = self.get(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        from app import db

        db.session.delete(user)
        db.session.commit()

    def find_by_username(self, username: str) -> User | None:
        """Buscar usuario por nombre de usuario"""
        return User.query.filter_by(username=username).first()

    def is_last_admin(self, user_id: int) -> bool:
        """Verificar si el usuario es el único administrador"""
        user = self.get(user_id)
        if not user or user.role.name != "Admin":
            return False

        admin_count = User.query.join(Role).filter(Role.name == "Admin").count()
        return admin_count == 1
