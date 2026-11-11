import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Config:
    """Базова конфігурація, спільна для всіх середовищ."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super_secret_key_123')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False

    # Лабораторна №5
    CONTACT_LOG = os.path.join(BASE_DIR, 'logs', 'contact.log')
    PRODUCTS_DB = os.path.join(BASE_DIR, 'data', 'products.json')
    PRODUCT_UPLOAD_FOLDER = None          # None -> app/products/static/uploads
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 МБ на запит (на файл — 2 МБ у формі)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'data.sqlite'),
    )


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'prod.sqlite'),
    )


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
