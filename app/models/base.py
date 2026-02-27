from abc import abstractmethod
from app import db


class BaseModel(db.Model):
    __abstract__ = True

    @abstractmethod
    def to_dict(self):
        """Representación serializable del modelo."""
        pass

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
