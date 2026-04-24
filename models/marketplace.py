from datetime import datetime
from . import db

class CropListing(db.Model):
    """Model for storing marketplace product listings."""
    __tablename__ = 'crop_listings'

    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    crop_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # kg/quintal/ton
    description = db.Column(db.Text, nullable=True)
    state = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    lat = db.Column(db.Float, nullable=True) # Geo-location
    lng = db.Column(db.Float, nullable=True)
    is_organic = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=True)
    contact_phone = db.Column(db.String(20), nullable=False)
    available_from = db.Column(db.Date, nullable=False)
    available_until = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CropListing {self.crop_name} by farmer {self.farmer_id}>'
