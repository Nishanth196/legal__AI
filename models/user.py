"""
User & Admin models
"""
from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(120), nullable=False)
    email       = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False, default='')
    role        = db.Column(db.Enum('user', 'admin'), default='user', nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    avatar      = db.Column(db.String(255), default='')
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    last_login  = db.Column(db.DateTime)

    # ── Relationships ─────────────────────────────────────────────────────────
    documents   = db.relationship('GeneratedDocument', backref='author',  lazy='dynamic')
    profile     = db.relationship('CompanyProfile',    backref='user',    uselist=False)
    notifications = db.relationship('Notification',    backref='user',    lazy='dynamic')
    activity_logs = db.relationship('ActivityLog',     backref='user',    lazy='dynamic')
    chat_history  = db.relationship('ChatHistory',     backref='user',    lazy='dynamic')
    downloads     = db.relationship('Download',        backref='user',    lazy='dynamic')

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_admin(self) -> bool:
        return self.role == 'admin'

    def unread_notifications(self):
        return self.notifications.filter_by(is_read=False).count()

    def __repr__(self):
        return f'<User {self.email}>'


class Notification(db.Model):
    __tablename__ = 'notifications'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message    = db.Column(db.String(500), nullable=False)
    type       = db.Column(db.Enum('success', 'info', 'warning', 'error'), default='info')
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action     = db.Column(db.String(100), nullable=False)
    details    = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Setting(db.Model):
    __tablename__ = 'settings'

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key     = db.Column(db.String(100), nullable=False)
    value   = db.Column(db.Text)

    __table_args__ = (db.UniqueConstraint('user_id', 'key', name='uq_user_setting'),)
