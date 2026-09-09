"""
LexReg AI – Flask Application Factory
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect

# ── Extension instances (bound to app in create_app) ─────────────────────────
db       = SQLAlchemy()
login_manager = LoginManager()
mail     = Mail()
bcrypt   = Bcrypt()
csrf     = CSRFProtect()


def create_app(config_name: str = 'default') -> Flask:
    app = Flask(__name__)

    # ── Config ────────────────────────────────────────────────────────────────
    from config import config
    app.config.from_object(config[config_name])

    # Create upload, generated-doc, dl, and charts directories
    os.makedirs(app.config['UPLOAD_FOLDER'],       exist_ok=True)
    os.makedirs(app.config['GENERATED_DOCS_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'dl'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'static', 'charts'), exist_ok=True)

    # ── Init extensions ───────────────────────────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view        = 'auth.login'
    login_manager.login_message     = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # ── User loader ───────────────────────────────────────────────────────────
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Register blueprints ───────────────────────────────────────────────────
    from routes.auth      import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.documents import documents_bp
    from routes.admin     import admin_bp
    from routes.api       import api_bp
    from routes.profile   import profile_bp
    from routes.chatbot   import chatbot_bp
    from routes.ml        import ml_bp
    from routes.dl        import dl_bp

    app.register_blueprint(auth_bp,      url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(documents_bp, url_prefix='/documents')
    app.register_blueprint(admin_bp,     url_prefix='/admin')
    app.register_blueprint(api_bp,       url_prefix='/api')
    app.register_blueprint(profile_bp,   url_prefix='/profile')
    app.register_blueprint(chatbot_bp,   url_prefix='/chatbot')
    app.register_blueprint(ml_bp,        url_prefix='/ml')
    app.register_blueprint(dl_bp,        url_prefix='/dl')

    # ── Root redirect ─────────────────────────────────────────────────────────
    from flask import redirect, url_for
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    # ── Jinja2 globals ────────────────────────────────────────────────────────
    from datetime import datetime
    @app.context_processor
    def inject_globals():
        return {'now': datetime.now()}

    # ── Shell context ─────────────────────────────────────────────────────────
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'app': app}

    # ── Create DB tables if not exist ─────────────────────────────────────────
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Warning: DB creation error (often safe to ignore if tables exist): {e}")
        _seed_default_data(app)

    return app


def _seed_default_data(app):
    """Insert default admin, company profile, and document templates."""
    from models.user import User
    from models.company import CompanyProfile
    from models.document import DocumentTemplate

    # ── Default admin account ─────────────────────────────────────────────────
    if not User.query.filter_by(email='admin@lexregai.com').first():
        admin = User(
            name     = 'Admin',
            email    = 'admin@lexregai.com',
            role     = 'admin',
            is_verified = True,
        )
        admin.set_password('Admin@123')
        db.session.add(admin)

    # ── Demo user ─────────────────────────────────────────────────────────────
    demo_user = User.query.filter_by(email='nishanth@novaspheretech.com').first()
    if not demo_user:
        demo_user = User(
            name     = 'Nishanth S',
            email    = 'nishanth@novaspheretech.com',
            role     = 'user',
            is_verified = True,
        )
        demo_user.set_password('Demo@123')
        db.session.add(demo_user)
        db.session.flush()

    # ── Demo company profile ──────────────────────────────────────────────────
    if demo_user and not CompanyProfile.query.filter_by(user_id=demo_user.id).first():
        profile = CompanyProfile(
            user_id         = demo_user.id,
            company_name    = 'NovaSphere Technologies Private Limited',
            business_type   = 'Software & IT Services',
            owner_name      = 'Nishanth S',
            designation     = 'Managing Director',
            email           = 'support@novaspheretech.com',
            phone           = '+91 9876543210',
            website         = 'www.novaspheretech.com',
            address         = 'No.18, Innovation Park, Coimbatore, Tamil Nadu, India – 641021',
            pan_number      = 'ABCDE1234F',
            gst_number      = '33ABCDE1234F1Z5',
            cin_number      = 'U72900TZ2025PTC123456',
            registration_date = '15-04-2025',
            authorized_signatory = 'Nishanth S',
        )
        db.session.add(profile)

    # ── Document templates ────────────────────────────────────────────────────
    templates = [
        ('GST Registration',           'compliance',   'gst_registration'),
        ('Business License',           'license',      'business_license'),
        ('Trade License',              'license',      'trade_license'),
        ('Import Export License',      'license',      'ie_license'),
        ('Company Registration',       'corporate',    'company_registration'),
        ('Partnership Agreement',      'agreement',    'partnership_agreement'),
        ('Non Disclosure Agreement',   'agreement',    'nda'),
        ('Privacy Policy',             'policy',       'privacy_policy'),
        ('Terms and Conditions',       'policy',       'terms_conditions'),
        ('Employee Agreement',         'hr',           'employee_agreement'),
        ('Offer Letter',               'hr',           'offer_letter'),
        ('Vendor Agreement',           'agreement',    'vendor_agreement'),
        ('Compliance Report',          'compliance',   'compliance_report'),
        ('Regulatory Submission',      'regulatory',   'regulatory_submission'),
        ('Tax Declaration',            'tax',          'tax_declaration'),
        ('Environmental Clearance',    'regulatory',   'env_clearance'),
        ('Factory License',            'license',      'factory_license'),
        ('ISO Compliance',             'compliance',   'iso_compliance'),
        ('MSME Registration',          'corporate',    'msme_registration'),
        ('Startup India Registration', 'corporate',    'startup_india'),
    ]
    for name, category, slug in templates:
        if not DocumentTemplate.query.filter_by(slug=slug).first():
            tpl = DocumentTemplate(name=name, category=category, slug=slug, is_active=True)
            db.session.add(tpl)

    db.session.commit()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    flask_app = create_app('development')
    flask_app.run(debug=True, host='0.0.0.0', port=5000)
