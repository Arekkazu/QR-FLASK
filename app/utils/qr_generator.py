import base64
import hashlib
import hmac
import io
import time

import qrcode
from PIL import Image


def generate_qr_token(user_id, secret_key, expiration=60):
    timestamp = int(time.time())
    payload = f"{user_id}:{timestamp}"
    signature = hmac.new(
        secret_key.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    return f"{payload}:{signature}"


def validate_qr_token(token, secret_key, tolerance=90):
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return None
        user_id_str, timestamp_str, signature = parts
        timestamp = int(timestamp_str)
    except (ValueError, IndexError):
        return None

    if time.time() - timestamp > tolerance:
        return None

    expected_sig = hmac.new(
        secret_key.encode(), f"{user_id_str}:{timestamp_str}".encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, signature):
        return None

    return int(user_id_str)


def generate_qr_image(token):
    """Genera una imagen QR en base64 a partir del token"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)

    # Crear imagen
    img = qr.make_image(fill_color="black", back_color="white")

    # Convertir a base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Codificar en base64
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return img_base64
