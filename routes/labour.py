import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.labour import LabourWorker
from ai_modules.aadhaar_verifier import AadhaarVerifier

labour_bp = Blueprint('labour', __name__, url_prefix='/labour')
aadhaar_verifier = AadhaarVerifier()

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
    existing = LabourWorker.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        work_type = request.form.get('work_type')
        daily_wage = request.form.get('daily_wage')
        address = request.form.get('address')
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        phone = request.form.get('phone')
        is_verified = request.form.get('is_verified') == 'true'
        
        if not all([work_type, daily_wage, address, lat, lng, phone]):
            flash("Please provide all details including work location address.", "danger")
            return redirect(url_for('labour.register_labour'))

        # Handle Profile Pic
        profile_pic_filename = existing.profile_pic if existing else None
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename:
                filename = secure_filename(f"profile_{uuid.uuid4().hex}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                profile_pic_filename = filename

        # Handle Aadhaar Pic (Permanent storage if needed)
        aadhaar_pic_filename = existing.aadhaar_pic if existing else None
        if 'aadhaar_pic' in request.files:
            file = request.files['aadhaar_pic']
            if file and file.filename:
                filename = secure_filename(f"aadhaar_{uuid.uuid4().hex}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                aadhaar_pic_filename = filename
            
        if existing:
            existing.work_type = work_type
            existing.daily_wage = float(daily_wage)
            existing.address = address
            existing.phone = phone
            existing.lat = float(lat)
            existing.lng = float(lng)
            existing.is_available = True
            existing.is_verified = is_verified
            existing.profile_pic = profile_pic_filename
            existing.aadhaar_pic = aadhaar_pic_filename
        else:
            new_worker = LabourWorker(
                user_id=current_user.id,
                name=current_user.name,
                work_type=work_type,
                daily_wage=float(daily_wage),
                address=address,
                phone=phone,
                lat=float(lat),
                lng=float(lng),
                is_verified=is_verified,
                profile_pic=profile_pic_filename,
                aadhaar_pic=aadhaar_pic_filename
            )
            db.session.add(new_worker)
            
        db.session.commit()
        flash("Labour profile updated successfully!", "success")
        return redirect(url_for('labour.find_labour'))
        
    return render_template('labour/register.html', existing=existing)

@labour_bp.route('/verify_aadhaar', methods=['POST'])
@login_required
def verify_aadhaar():
    """AI Endpoint to verify Aadhaar photo against user name."""
    if 'aadhaar_photo' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['aadhaar_photo']
    if not file or not file.filename:
        return jsonify({'success': False, 'message': 'Invalid file'})

    # Save to temp
    temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"temp_aadhaar_{uuid.uuid4().hex}.jpg")
    file.save(temp_path)
    
    try:
        # Verify using AI
        result = aadhaar_verifier.verify(temp_path, current_user.name)
        
        # Cleanup temp file if you want, or leave for audit
        # os.remove(temp_path) 
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@labour_bp.route('/toggle_availability', methods=['POST'])
@login_required
def toggle_availability():
    worker = LabourWorker.query.filter_by(user_id=current_user.id).first()
    if worker:
        worker.is_available = not worker.is_available
        db.session.commit()
        return jsonify({'status': 'success', 'available': worker.is_available})
    return jsonify({'status': 'error'}), 404
