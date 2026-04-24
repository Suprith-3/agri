from datetime import datetime
from . import db

class UserVerification(db.Model):
    """Model to store user identity proof for rentals."""
    __tablename__ = 'user_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dl_number = db.Column(db.String(50), nullable=False)
    dl_photo_url = db.Column(db.String(500), nullable=False)
    aadhar_number = db.Column(db.String(12), nullable=False)
    aadhar_photo_url = db.Column(db.String(500), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RentalItem(db.Model):
    """Items available for rent (Tractors, Tools, etc.)"""
    __tablename__ = 'rental_items'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50)) # e.g. Machinery, Tools, Irrigation
    
    # Pricing
    hourly_rate = db.Column(db.Float, default=0.0)
    daily_rate = db.Column(db.Float, default=0.0)
    
    image_url = db.Column(db.String(500))
    location = db.Column(db.String(100))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RentalBooking(db.Model):
    """Track rental transactions."""
    __tablename__ = 'rental_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('rental_items.id'), nullable=False)
    renter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
