from datetime import datetime
from . import db

class Course(db.Model):
    """Model for a 'Classroom' where farmers can learn."""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50)) 
    class_code = db.Column(db.String(10), unique=True) # Unique join code
    instructor_name = db.Column(db.String(100))
    thumbnail_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Lessons in this course
    lessons = db.relationship('Lesson', backref='course', lazy=True, cascade="all, delete-orphan")

class Lesson(db.Model):
    """Individual materials/lessons within a course."""
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text) # Markdown or HTML content
    material_type = db.Column(db.String(50), default='reading') # video, reading, quiz
    external_link = db.Column(db.String(500)) # Link to YouTube or PDF
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
