from app import create_app
from models import db
from models.education import Course, Lesson

app = create_app()

with app.app_context():
    # 1. Create the Official Host Classroom
    course = Course(
        title='Advanced Organic Farming 2024',
        description='Master class by Agricultural Experts on organic pesticides and soil health.',
        category='Organic Farming',
        instructor_name='Dr. Agri Guru'
    )
    db.session.add(course)
    db.session.commit()
    
    # 2. Add an Official Video Material
    lesson1 = Lesson(
        course_id=course.id,
        title='How to Prepare Organic Nitrogen Fertilizer',
        content="In this video, I will show you exactly how to mix organic compost for maximum nitrogen. This is essential for the vegetative stage of your crops.",
        material_type='video',
        external_link='https://www.youtube.com/watch?v=R3n0q6WzWv4'
    )
    
    # 3. Add an Information Guide
    lesson2 = Lesson(
        course_id=course.id,
        title='Soil Health Checklist',
        content="""
        <h3>Official Soil Checklist</h3>
        <ul>
            <li>Check PH balance every month.</li>
            <li>Ensure proper drainage to avoid root rot.</li>
            <li>Use Green Manure before the next sowing season.</li>
        </ul>
        """,
        material_type='reading'
    )
    
    db.session.add(lesson1)
    db.session.add(lesson2)
    db.session.commit()
    
    print("--------------------------------------------------")
    print("[Classroom] Success: Host Classroom & Videos Created!")
    print("--------------------------------------------------")
