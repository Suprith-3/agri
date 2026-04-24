from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.education import Course, Lesson

education_bp = Blueprint('education', __name__, url_prefix='/learn')

@education_bp.route('/')
@login_required
def home():
    """Main page showing available classes."""
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('education/home.html', courses=courses)

@education_bp.route('/course/<int:course_id>')
@login_required
def course_detail(course_id):
    """The 'Stream' view of a classroom."""
    course = Course.query.get_or_404(course_id)
    # Get recent materials for the stream
    stream_items = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.created_at.desc()).limit(10).all()
    return render_template('education/course_stream.html', course=course, stream_items=stream_items)

@education_bp.route('/course/<int:course_id>/classwork')
@login_required
def classwork(course_id):
    """The organized list of lessons."""
    course = Course.query.get_or_404(course_id)
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order.asc()).all()
    return render_template('education/classwork.html', course=course, lessons=lessons)

@education_bp.route('/lesson/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    """View specific material/lesson content."""
    lesson = Lesson.query.get_or_404(lesson_id)
    return render_template('education/lesson_view.html', lesson=lesson)

import uuid

@education_bp.route('/course/join', methods=['POST'])
@login_required
def join_class():
    code = request.form.get('class_code').upper().strip()
    course = Course.query.filter_by(class_code=code).first()
    if course:
        flash(f'Successfully joined {course.title}!', 'success')
        return redirect(url_for('education.course_detail', course_id=course.id))
    flash('Invalid Class Code. Please check and try again.', 'danger')
    return redirect(url_for('education.home'))

# Teacher Actions
@education_bp.route('/course/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        
        # Generate short unique code
        code = str(uuid.uuid4()).upper()[:8]
        
        new_course = Course(
            title=title,
            description=description,
            category=category,
            class_code=code,
            instructor_name=current_user.name
        )
        db.session.add(new_course)
        db.session.commit()
        flash(f'Class "{title}" created! Your Join Code is: {code}', 'success')
        return redirect(url_for('education.home'))
        
    return render_template('education/create_course.html')

@education_bp.route('/course/<int:course_id>/add-lesson', methods=['GET', 'POST'])
@login_required
def add_lesson(course_id):
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        material_type = request.form.get('material_type')
        link = request.form.get('external_link')
        
        new_lesson = Lesson(
            course_id=course_id,
            title=title,
            content=content,
            material_type=material_type,
            external_link=link
        )
        db.session.add(new_lesson)
        db.session.commit()
        flash('Material posted to classwork!', 'success')
        return redirect(url_for('education.classwork', course_id=course_id))
        
    course = Course.query.get_or_404(course_id)
    return render_template('education/add_lesson.html', course=course)
