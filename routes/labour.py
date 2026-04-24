from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.labour import LabourWorker

labour_bp = Blueprint('labour', __name__, url_prefix='/labour')

@labour_bp.route('/')
@login_required
def find_labour():
    """Map view to find available labour."""
    workers = LabourWorker.query.filter_by(is_available=True).all()
    map_data = [w.to_dict() for w in workers]
    return render_template('labour/map.html', map_data=map_data)

@labour_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register_labour():
    """Register as a labourer."""
    # Check if user already has a profile
    existing = LabourWorker.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        work_type = request.form.get('work_type')
        daily_wage = request.form.get('daily_wage')
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        phone = request.form.get('phone')
        
        if not all([work_type, daily_wage, lat, lng, phone]):
            flash("Please provide all details including live location.", "danger")
            return redirect(url_for('labour.register_labour'))
            
        if existing:
            existing.work_type = work_type
            existing.daily_wage = float(daily_wage)
            existing.phone = phone
            existing.lat = float(lat)
            existing.lng = float(lng)
            existing.is_available = True
        else:
            new_worker = LabourWorker(
                user_id=current_user.id,
                name=current_user.name,
                work_type=work_type,
                daily_wage=float(daily_wage),
                phone=phone,
                lat=float(lat),
                lng=float(lng)
            )
            db.session.add(new_worker)
            
        db.session.commit()
        flash("Labour profile updated successfully!", "success")
        return redirect(url_for('labour.find_labour'))
        
    return render_template('labour/register.html', existing=existing)

@labour_bp.route('/toggle_availability', methods=['POST'])
@login_required
def toggle_availability():
    worker = LabourWorker.query.filter_by(user_id=current_user.id).first()
    if worker:
        worker.is_available = not worker.is_available
        db.session.commit()
        return jsonify({'status': 'success', 'available': worker.is_available})
    return jsonify({'status': 'error'}), 404
