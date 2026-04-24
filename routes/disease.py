import os
import uuid
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.crop import DiseaseDetection
from ai_modules.disease_detector import DiseaseDetector

disease_bp = Blueprint('disease', __name__, url_prefix='/disease')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@disease_bp.route('/detect', methods=['GET', 'POST'])
@login_required
def detect():
    """Handle crop disease detection mapping."""
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
            
            # Ensure folder exists
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(filepath)
                
                # Run the model
                detector = DiseaseDetector()
                disease_name, confidence = detector.predict(filepath)
                
                # Get Gemini AI Advice
                treatment_advice = detector.get_ai_treatment(disease_name, confidence)
                
                # Save to DB
                detection = DiseaseDetection(
                    user_id=current_user.id,
                    image_path=filename,
                    disease_name=disease_name,
                    confidence=confidence,
                    treatment=treatment_advice
                )
                db.session.add(detection)
                db.session.commit()
                
                flash('Detection completed successfully!', 'success')
                return redirect(url_for('disease.result', detection_id=detection.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error processing image: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('Invalid file format. Please upload JPG, PNG or WEBP.', 'danger')
            
    return render_template('disease/upload.html')

@disease_bp.route('/result/<int:detection_id>')
@login_required
def result(detection_id):
    """View prediction result."""
    detection = DiseaseDetection.query.get_or_404(detection_id)
    if detection.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard.home'))
        
    return render_template('disease/result.html', detection=detection)
