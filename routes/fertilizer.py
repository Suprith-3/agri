from flask import Blueprint, render_template, request, flash, current_app
from flask_login import login_required
from ai_modules.fertilizer_scanner import FertilizerScanner
import os
from werkzeug.utils import secure_filename
import time

fertilizer_bp = Blueprint('fertilizer', __name__, url_prefix='/fertilizer')

@fertilizer_bp.route('/scan', methods=['GET', 'POST'])
@login_required
def scan():
    """Handle fertilizer scanning via image upload/camera."""
    result_data = None
    image_url = None
    
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No image uploaded', 'warning')
            return render_template('fertilizer/scan.html')
            
        file = request.files['image']
        if file.filename == '':
            flash('No selected file', 'warning')
            return render_template('fertilizer/scan.html')

        if file:
            filename = secure_filename(f"fertilizer_{int(time.time())}.jpg")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # For displaying back to user
            image_url = f"uploads/{filename}"
            
            try:
                api_key = current_app.config.get('OPENROUTER_API_KEY')
                scanner = FertilizerScanner(api_key=api_key)
                result_data = scanner.scan(filepath)
                flash('Scan completed!', 'success')
            except Exception as e:
                flash(f'Scan failed: {str(e)}', 'danger')

    return render_template('fertilizer/scan.html', result_data=result_data, image_url=image_url)
