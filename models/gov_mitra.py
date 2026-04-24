from datetime import datetime
from . import db

class QuarterlySurvey(db.Model):
    """Model for tracking quarterly government surveys of farmers."""
    __tablename__ = 'quarterly_surveys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quarter = db.Column(db.Integer, nullable=False) # 1 (Jan-Mar), 2 (Apr-Jun), etc.
    year = db.Column(db.Integer, nullable=False)
    
    # Crop & Financial Information
    crop_grown = db.Column(db.String(100))
    revenue = db.Column(db.Float, default=0.0)
    expenses = db.Column(db.Float, default=0.0)
    profit_loss = db.Column(db.Float, default=0.0)
    
    # Biometric & Personnel Information (Local system references)
    face_scan_verified = db.Column(db.Boolean, default=False)
    biometric_ref_id = db.Column(db.String(255), nullable=True)
    collecting_official = db.Column(db.String(100))
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    farmer = db.relationship('User', backref=db.backref('surveys', lazy=True))

    def __repr__(self):
        return f'<Survey {self.user_id} Q{self.quarter} {self.year}>'
