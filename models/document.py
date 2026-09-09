"""
Document Template and Generated Document models
"""
from datetime import datetime
from app import db


class DocumentTemplate(db.Model):
    __tablename__ = 'document_templates'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    category    = db.Column(db.String(100))
    slug        = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon        = db.Column(db.String(50), default='fa-file-alt')
    is_active   = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    documents = db.relationship('GeneratedDocument', backref='template', lazy='dynamic')

    # Icon mapping per category
    ICONS = {
        'compliance':  'fa-shield-alt',
        'license':     'fa-certificate',
        'corporate':   'fa-building',
        'agreement':   'fa-handshake',
        'policy':      'fa-file-contract',
        'hr':          'fa-users',
        'regulatory':  'fa-landmark',
        'tax':         'fa-calculator',
    }

    def get_icon(self):
        return self.ICONS.get(self.category, 'fa-file-alt')


class GeneratedDocument(db.Model):
    __tablename__ = 'generated_documents'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('document_templates.id'))
    title       = db.Column(db.String(300), nullable=False)
    content     = db.Column(db.Text)
    status      = db.Column(db.Enum('draft', 'generated', 'completed'), default='draft')
    pdf_path    = db.Column(db.String(255))
    docx_path   = db.Column(db.String(255))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    downloads = db.relationship('Download', backref='document', lazy='dynamic')

    def status_badge(self):
        badges = {
            'draft':     'warning',
            'generated': 'info',
            'completed': 'success',
        }
        return badges.get(self.status, 'secondary')


class Download(db.Model):
    __tablename__ = 'downloads'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_id   = db.Column(db.Integer, db.ForeignKey('generated_documents.id'), nullable=False)
    format        = db.Column(db.Enum('pdf', 'docx'), nullable=False)
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatHistory(db.Model):
    __tablename__ = 'chat_history'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message    = db.Column(db.Text, nullable=False)
    response   = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
