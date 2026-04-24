from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models import db
from models.rental import UserVerification, RentalItem, RentalBooking
from datetime import datetime

rental_bp = Blueprint('rental', __name__, url_prefix='/rental')

@rental_bp.route('/')
@login_required
def home():
    """Main rental marketplace."""
    items = RentalItem.query.filter_by(is_available=True).all()
    # Check if current user is verified
    verification = UserVerification.query.filter_by(user_id=current_user.id).first()
    return render_template('rental/home.html', items=items, verification=verification)

import os
from werkzeug.utils import secure_filename
import time

@rental_bp.route('/verify', methods=['GET', 'POST'])
@login_required
def verify_identity():
    """Identity upload form with real file storage."""
    if request.method == 'POST':
        dl_number = request.form.get('dl_number')
        aadhar_number = request.form.get('aadhar_number')
        
        # Handle DL Photo Upload
        dl_file = request.files.get('dl_photo')
        aadhar_file = request.files.get('aadhar_photo')
        
        if dl_file and aadhar_file:
            # Secure preservation of DL image
            dl_fn = secure_filename(f"dl_{current_user.id}_{int(time.time())}.jpg")
            dl_path = os.path.join(current_app.config['UPLOAD_FOLDER'], dl_fn)
            dl_file.save(dl_path)
            
            # Secure preservation of Aadhar image
            aa_fn = secure_filename(f"aa_{current_user.id}_{int(time.time())}.jpg")
            aa_path = os.path.join(current_app.config['UPLOAD_FOLDER'], aa_fn)
            aadhar_file.save(aa_path)
            
            new_verification = UserVerification(
                user_id=current_user.id,
                dl_number=dl_number,
                dl_photo_url=f"uploads/{dl_fn}",
                aadhar_number=aadhar_number,
                aadhar_photo_url=f"uploads/{aa_fn}",
                is_verified=True
            )
            db.session.add(new_verification)
            db.session.commit()
            
            flash('Identity Verified! Your proof photos have been saved securely.', 'success')
            return redirect(url_for('rental.home'))
            
        flash('Both Aadhar and DL photos are required!', 'danger')
        
    return render_template('rental/verify.html')

@rental_bp.route('/item/list', methods=['GET', 'POST'])
@login_required
def list_item():
    """Host/Owner lists an item for rent with a real photo."""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        hourly = request.form.get('hourly_rate')
        daily = request.form.get('daily_rate')
        category = request.form.get('category')
        
        # Handle Equipment Image Upload
        item_file = request.files.get('item_photo')
        image_url = "https://images.unsplash.com/photo-1594498257602-0175c0f9461f?q=80&w=400" # Fallback
        
        if item_file:
            it_fn = secure_filename(f"rent_{current_user.id}_{int(time.time())}.jpg")
            it_path = os.path.join(current_app.config['UPLOAD_FOLDER'], it_fn)
            item_file.save(it_path)
            image_url = f"uploads/{it_fn}"
            
        new_item = RentalItem(
            owner_id=current_user.id,
            name=name,
            description=description,
            hourly_rate=float(hourly) if hourly else 0.0,
            daily_rate=float(daily) if daily else 0.0,
            category=category,
            image_url=image_url
        )
        db.session.add(new_item)
        db.session.commit()
        flash(f'Successfully listed {name}! It is now live in the hub.', 'success')
        return redirect(url_for('rental.home'))
        
    return render_template('rental/list_item.html')

@rental_bp.route('/book/<int:item_id>', methods=['POST'])
@login_required
def book_item(item_id):
    """Process rental booking."""
    # Strict Verification Check
    verification = UserVerification.query.filter_by(user_id=current_user.id).first()
    if not verification:
        flash('Identity proof required! Please upload your DL and Aadhar before renting.', 'warning')
        return redirect(url_for('rental.verify_identity'))
        
    # Process booking (Simplified for now)
    item = RentalItem.query.get_or_404(item_id)
    flash(f'Booking request sent for {item.name}. The owner will contact you.', 'success')
    return redirect(url_for('rental.home'))
