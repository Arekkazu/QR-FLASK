import time

from app.services.base_service import BaseService
from app.utils.qr_generator import (
    generate_qr_image,
    generate_qr_token,
    validate_qr_token,
)


class QRService(BaseService):
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def create_qr_data(self, user_id):
        """Genera el token para el QR del usuario."""
        token = generate_qr_token(user_id, self.secret_key)
        return {"token": token, "image": generate_qr_image(token)}

    def validate_qr_data(self, token):
        """Valida el token del QR escaneado."""
        return validate_qr_token(token, self.secret_key)

    # Métodos abstractos no implementados (no son necesarios para este servicio)
    def create(self, *args, **kwargs):
        raise NotImplementedError("QRService does not implement create method")

    def update(self, *args, **kwargs):
        raise NotImplementedError("QRService does not implement update method")

    def delete(self, *args, **kwargs):
        raise NotImplementedError("QRService does not implement delete method")

    def get(self, *args, **kwargs):
        raise NotImplementedError("QRService does not implement get method")
