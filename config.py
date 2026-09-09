import os
from datetime import timedelta

class Config:
    # ─── Secret & Security ───────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'lexreg-secret-key-change-in-production-2025')
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # ─── Database ─────────────────────────────────────────────────────────
    DB_TYPE     = os.environ.get('DB_TYPE',     'sqlite') # default to sqlite for easy setup, can be set to 'mysql'
    DB_HOST     = os.environ.get('DB_HOST',     'localhost')
    DB_PORT     = os.environ.get('DB_PORT',     '3306')
    DB_USER     = os.environ.get('DB_USER',     'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME     = os.environ.get('DB_NAME',     'lexreg_db')

    if DB_TYPE == 'mysql':
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    else:
        # Fallback to local SQLite database
        db_path = os.path.join(os.path.dirname(__file__), 'lexreg.db')
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    } if DB_TYPE == 'mysql' else {}

    # ─── Session ──────────────────────────────────────────────────────────
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # ─── Google Gemini API ────────────────────────────────────────────────
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL   = 'gemini-1.5-flash'

    # ─── Mail (Flask-Mail) ────────────────────────────────────────────────
    MAIL_SERVER   = os.environ.get('MAIL_SERVER',   'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@lexregai.com')

    # ─── File Uploads ─────────────────────────────────────────────────────
    UPLOAD_FOLDER    = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

    # ─── Generated Docs ───────────────────────────────────────────────────
    GENERATED_DOCS_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'generated')

    # ─── Pagination ───────────────────────────────────────────────────────
    DOCS_PER_PAGE = 10

    # ─── Demo Company ─────────────────────────────────────────────────────
    DEMO_COMPANY = {
        'name':        'NovaSphere Technologies Private Limited',
        'type':        'Software & IT Services',
        'owner':       'Nishanth S',
        'designation': 'Managing Director',
        'email':       'support@novaspheretech.com',
        'phone':       '+91 9876543210',
        'website':     'www.novaspheretech.com',
        'address':     'No.18, Innovation Park, Coimbatore, Tamil Nadu, India – 641021',
        'pan':         'ABCDE1234F',
        'gst':         '33ABCDE1234F1Z5',
        'cin':         'U72900TZ2025PTC123456',
        'reg_date':    '15-04-2025',
        'signatory':   'Nishanth S',
    }


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
