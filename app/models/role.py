from app import db
from app.models.base import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # 'Admin', 'User'

    def to_dict(self):
        return {"id": self.id, "name": self.name}
