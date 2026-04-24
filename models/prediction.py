from datetime import datetime
from . import db

class YieldPrediction(db.Model):
    """Model for storing yield prediction history."""
    __tablename__ = 'yield_predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    crop = db.Column(db.String(100), nullable=False)
    area = db.Column(db.Float, nullable=False)
    soil_type = db.Column(db.String(100), nullable=False)
    irrigation = db.Column(db.String(100), nullable=False)
    predicted_yield = db.Column(db.Float, nullable=False)
    estimated_revenue = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatHistory(db.Model):
    """Model for storing chatbot history."""
    __tablename__ = 'chat_histories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class MarketRate(db.Model):
    """Model for storing actual APMC market rates."""
    __tablename__ = 'market_rates'

    id = db.Column(db.Integer, primary_key=True)
    crop = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    mandi = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    arrival_quantity = db.Column(db.String(50), nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
