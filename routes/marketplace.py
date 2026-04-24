import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.marketplace import CropListing

marketplace_bp = Blueprint('marketplace', __name__, url_prefix='/marketplace')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@marketplace_bp.route('/')
def browse():
    """Browse all marketplace listings."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')
    state = request.args.get('state', '')
    
    query = CropListing.query.filter_by(is_available=True)
    if search:
        query = query.filter(CropListing.crop_name.ilike(f'%{search}%'))
    if state:
        query = query.filter(CropListing.state.ilike(f'%{state}%'))
        
    query = query.order_by(CropListing.created_at.desc())
    listings = query.paginate(page=page, per_page=12, error_out=False)
    
    return render_template('marketplace/listings.html', listings=listings, current_search=search)

@marketplace_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_listing():
    """Add a new crop listing."""
    if request.method == 'POST':
        try:
            filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '' and allowed_file(file.filename):
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = secure_filename(f"market_{uuid.uuid4().hex}.{ext}")
                    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            
            new_listing = CropListing(
                farmer_id=current_user.id,
                crop_name=request.form.get('crop_name'),
                quantity=int(request.form.get('quantity')),
                price=float(request.form.get('price')),
                unit=request.form.get('unit'),
                description=request.form.get('description'),
                state=request.form.get('state'),
                district=request.form.get('district'),
                is_organic='is_organic' in request.form,
                contact_phone=request.form.get('contact_phone'),
                available_from=datetime.strptime(request.form.get('available_from'), '%Y-%m-%d'),
                available_until=datetime.strptime(request.form.get('available_until'), '%Y-%m-%d'),
                image_path=filename,
                lat=float(request.form.get('lat')) if request.form.get('lat') else None,
                lng=float(request.form.get('lng')) if request.form.get('lng') else None
            )
            
            db.session.add(new_listing)
            db.session.commit()
            
            flash('Your product was listed successfully!', 'success')
            return redirect(url_for('marketplace.my_listings'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('marketplace/add_listing.html')

@marketplace_bp.route('/my')
@login_required
def my_listings():
    """Show farmer's own listings."""
    listings = CropListing.query.filter_by(farmer_id=current_user.id).order_by(CropListing.created_at.desc()).all()
    return render_template('marketplace/my_listings.html', listings=listings)

@marketplace_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_listing(id):
    """Delete a listing using POST route."""
    listing = CropListing.query.get_or_404(id)
    if listing.farmer_id != current_user.id:
        flash('Unauthorized permission.', 'danger')
        return redirect(url_for('marketplace.my_listings'))
        
    db.session.delete(listing)
    db.session.commit()
    flash('Listing deleted.', 'success')
    return redirect(url_for('marketplace.my_listings'))

@marketplace_bp.route('/map')
def map_view():
    """Show all current listings on a map."""
    listings = CropListing.query.filter_by(is_available=True).all()
    # Prepare serializable data for JS
    map_data = []
    for l in listings:
        if l.lat and l.lng:
            map_data.append({
                'id': l.id,
                'name': l.crop_name,
                'price': l.price,
                'unit': l.unit,
                'lat': l.lat,
                'lng': l.lng,
                'image': l.image_path
            })
    return render_template('marketplace/map.html', map_data=map_data)

@marketplace_bp.route('/<int:id>')
def detail(id):
    """View a listing's specific detail page."""
    listing = CropListing.query.get_or_404(id)
    # Get 3 related listings in same state
    related = CropListing.query.filter(CropListing.state == listing.state, CropListing.id != listing.id).limit(3).all()
    return render_template('marketplace/detail.html', listing=listing, related=related)
