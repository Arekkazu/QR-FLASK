#!/usr/bin/env python3
"""
Script de inicio para el Sistema de Asistencias QR
"""

import os
import sys

from app import create_app


def main():
    """Función principal para iniciar el servidor"""

    # Configurar variables de entorno por defecto
    os.environ.setdefault("FLASK_ENV", "development")
    os.environ.setdefault("FLASK_RUN_HOST", "0.0.0.0")
    os.environ.setdefault("FLASK_RUN_PORT", "5000")

    # Crear la aplicación
    try:
        app = create_app()
        print("=" * 60)
        print("🚀 SISTEMA DE ASISTENCIAS QR")
        print("=" * 60)
        print("✅ Aplicación inicializada correctamente")
        print(f"🌐 Servidor ejecutándose en: http://localhost:5000")
        print("📱 Usuarios de prueba:")
        print("   👑 Admin: admin / admin123")
        print("   👤 Usuario: usuario / usuario123")
        print("=" * 60)
        print("Presiona Ctrl+C para detener el servidor")
        print("=" * 60)

        # Ejecutar la aplicación
        app.run(
            host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
            port=int(os.getenv("FLASK_RUN_PORT", 5000)),
            debug=app.config.get("DEBUG", True),
        )

    except Exception as e:
        print(f"❌ Error al iniciar la aplicación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
