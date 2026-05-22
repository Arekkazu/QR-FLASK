from app.services.base_service import BaseService
from app.models.attendance import Attendance
from app.models.user import User
from datetime import date
from app import db


class AttendanceService(BaseService):
    def create(self, user_id: int) -> Attendance:
        """Crear un nuevo registro de asistencia"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Usuario no existe")

        today = date.today()
        existing_attendance = Attendance.query.filter_by(
            user_id=user_id, date=today
        ).first()

        if existing_attendance:
            raise ValueError("Ya se registró asistencia para este usuario hoy")

        attendance = Attendance(user_id=user_id)
        db.session.add(attendance)
        db.session.commit()
        return attendance

    def get(self, attendance_id: int) -> Attendance | None:
        """Obtener un registro de asistencia por ID"""
        return Attendance.query.get(attendance_id)

    def get_all(self) -> list[Attendance]:
        """Obtener todos los registros de asistencia"""
        return Attendance.query.all()

    def get_recent(self, limit: int = 10) -> list[Attendance]:
        """Obtener los registros más recientes (por timestamp desc)"""
        return (
            Attendance.query.order_by(Attendance.timestamp.desc()).limit(limit).all()
        )

    def update(self, attendance_id: int, **kwargs) -> None:
        """Actualizar un registro de asistencia existente"""
        # No se permite actualizar un registro de asistencia
        raise NotImplementedError(
            "Los registros de asistencia no pueden ser actualizados"
        )

    def delete(self, attendance_id: int) -> None:
        """Eliminar un registro de asistencia"""
        attendance = self.get(attendance_id)
        if not attendance:
            raise ValueError("Registro de asistencia no encontrado")

        db.session.delete(attendance)
        db.session.commit()

    def get_for_user_on_date(self, user_id: int, date_obj: date) -> Attendance | None:
        """Obtener asistencia de un usuario en una fecha específica"""
        return Attendance.query.filter_by(user_id=user_id, date=date_obj).first()

    def get_user_attendance(self, user_id: int) -> list[Attendance]:
        """Obtener historial de asistencias de un usuario"""
        return (
            Attendance.query.filter_by(user_id=user_id)
            .order_by(Attendance.date.desc())
            .all()
        )
