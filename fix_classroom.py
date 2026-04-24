from app import create_app
from models import db
from models.education import Course, Lesson
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("[DB] Dropping old classroom tables...")
    try:
        # Drop dependent table first
        db.session.execute(text('DROP TABLE IF EXISTS lessons CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS courses CASCADE'))
        db.session.commit()
    except Exception as e:
        print(f"[DB] Notice: {e}")
        
    print("[DB] Creating new Styled Classroom tables...")
    db.create_all()
    
    # Add the sample Dronacharya class
    c = Course(
        title='Advanced Rice Tech Masterclass', 
        class_code='D7X2B9A1', 
        instructor_name='Dr. Agri Guru', 
        category='Integrated Farming',
        description='Learn how to double your yield using the latest Dronacharya techniques.'
    )
    db.session.add(c)
    db.session.commit()
    
    print("--------------------------------------------------")
    print("SUCCESS: Classroom Tables Re-created with Class Codes!")
    print("Your first Class Code is: D7X2B9A1")
    print("--------------------------------------------------")
