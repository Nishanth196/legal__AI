"""
Company Profile model
"""
from datetime import datetime
from app import db


class CompanyProfile(db.Model):
    __tablename__ = 'company_profile'

    id                   = db.Column(db.Integer, primary_key=True)
    user_id              = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    company_name         = db.Column(db.String(200), nullable=False)
    business_type        = db.Column(db.String(100))
    owner_name           = db.Column(db.String(120))
    designation          = db.Column(db.String(100))
    email                = db.Column(db.String(150))
    phone                = db.Column(db.String(20))
    website              = db.Column(db.String(200))
    address              = db.Column(db.Text)
    pan_number           = db.Column(db.String(20))
    gst_number           = db.Column(db.String(20))
    cin_number           = db.Column(db.String(30))
    registration_date    = db.Column(db.String(20))
    authorized_signatory = db.Column(db.String(120))
    logo_path            = db.Column(db.String(255))
    seal_path            = db.Column(db.String(255))
    updated_at           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'company_name':         self.company_name,
            'business_type':        self.business_type,
            'owner_name':           self.owner_name,
            'designation':          self.designation,
            'email':                self.email,
            'phone':                self.phone,
            'website':              self.website,
            'address':              self.address,
            'pan_number':           self.pan_number,
            'gst_number':           self.gst_number,
            'cin_number':           self.cin_number,
            'registration_date':    self.registration_date,
            'authorized_signatory': self.authorized_signatory,
        }
