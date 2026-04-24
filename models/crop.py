from datetime import datetime
from . import db

class DiseaseDetection(db.Model):
    """Model for storing crop disease detection history."""
    __tablename__ = 'disease_detections'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    disease_name = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    treatment = db.Column(db.Text, nullable=True)  # JSON or structured text from Gemini
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DiseaseDetection {self.disease_name} at {self.detected_at}>'
