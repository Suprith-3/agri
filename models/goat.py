from datetime import datetime
from . import db

class GoatExpert(db.Model):
    """The 20 Pre-defined Agricultural Legends."""
    __tablename__ = 'goat_experts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200)) # e.g., Father of Green Revolution
    description = db.Column(db.Text)
    specialty = db.Column(db.String(100))
    image_url = db.Column(db.String(500))
    schedule_time = db.Column(db.String(100)) # e.g., Every Monday 6 PM
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GoatUnlock(db.Model):
    """Tracks ₹1 payments per user per expert."""
    __tablename__ = 'goat_unlocks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expert_id = db.Column(db.Integer, db.ForeignKey('goat_experts.id'), nullable=False)
    payment_id = db.Column(db.String(100)) # Razorpay Payment ID
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
