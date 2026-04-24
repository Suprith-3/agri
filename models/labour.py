from . import db
from datetime import datetime

class LabourWorker(db.Model):
    __tablename__ = 'labour_workers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    work_type = db.Column(db.String(100), nullable=False)  # e.g., Harvesting, Plowing, Sowing
    daily_wage = db.Column(db.Float, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    
    # Geolocation
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    
    is_available = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    profile_pic = db.Column(db.String(255), nullable=True)
    aadhaar_pic = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to user
    user = db.relationship('User', backref=db.backref('labour_profile', uselist=False))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'work_type': self.work_type,
            'daily_wage': self.daily_wage,
            'phone': self.phone,
            'address': self.address,
            'lat': self.lat,
            'lng': self.lng,
            'is_available': self.is_available,
            'is_verified': self.is_verified,
            'profile_pic': self.profile_pic
        }
