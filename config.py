import os
from dotenv import load_dotenv

load_dotenv()  # Cargar variables de entorno desde .env


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev_secret_key_very_random"
    QR_SECRET_KEY = os.environ.get("QR_SECRET_KEY") or "dev_qr_secret_key_very_random"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    QR_EXPIRATION = int(os.environ.get("QR_EXPIRATION", 60))  # segundos


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Diccionario de configuraciones accesible desde fuera
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
