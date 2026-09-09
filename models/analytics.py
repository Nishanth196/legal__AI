"""
Analytics model
"""
from datetime import datetime, date
from app import db


class Analytics(db.Model):
    __tablename__ = 'analytics'

    id           = db.Column(db.Integer, primary_key=True)
    date         = db.Column(db.Date, unique=True, nullable=False, default=date.today)
    total_users  = db.Column(db.Integer, default=0)
    total_docs   = db.Column(db.Integer, default=0)
    api_calls    = db.Column(db.Integer, default=0)
    downloads    = db.Column(db.Integer, default=0)

    @classmethod
    def today(cls):
        today = date.today()
        record = cls.query.filter_by(date=today).first()
        if not record:
            record = cls(date=today)
            db.session.add(record)
            db.session.commit()
        return record

    @classmethod
    def increment(cls, field: str, amount: int = 1):
        record = cls.today()
        setattr(record, field, getattr(record, field) + amount)
        db.session.commit()
