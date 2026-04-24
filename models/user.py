from datetime import datetime
from flask_login import UserMixin
from . import db

class User(db.Model, UserMixin):
    """User model for storing farmer and admin information."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    farm_size = db.Column(db.Float, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    role = db.Column(db.String(20), default='farmer')  # farmer/admin

    # Relationships
    chat_histories = db.relationship('ChatHistory', backref='user', lazy=True)
    yield_predictions = db.relationship('YieldPrediction', backref='user', lazy=True)
    listings = db.relationship('CropListing', backref='farmer', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'
