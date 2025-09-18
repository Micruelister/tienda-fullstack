import os
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env
load_dotenv()

class Config:
    """Clase base de configuración."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de sesión
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'None'

    # Carpeta de subida de archivos
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__name__)), 'app/static/uploads/products')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Configuración de Stripe
    STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

    # Configuración de CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173')


class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__name__)), 'app.db')

class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # En producción, podrías querer usar Redis para las sesiones
    # SESSION_TYPE = 'redis'
    # SESSION_REDIS = redis.from_url(os.environ.get('SESSION_REDIS_URL'))

# Un diccionario para seleccionar la configuración a través de una variable de entorno
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
