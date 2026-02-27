from datetime import datetime, date
from app import db
from app.models.base import BaseModel


class Attendance(BaseModel):
    __tablename__ = "attendances"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    date = db.Column(db.Date, default=date.today)  # Para unicidad diaria

    # Restricción única: un registro por usuario por día
    __table_args__ = (
        db.UniqueConstraint("user_id", "date", name="unique_daily_attendance"),
    )

    def to_dict(self) -> dict:
        """Representación serializable del modelo"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "date": self.date.isoformat() if self.date else None,
        }

    def __repr__(self) -> str:
        return f"<Attendance user_id={self.user_id} date={self.date}>"
