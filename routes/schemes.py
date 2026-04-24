from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db
from models.scheme import GovernmentScheme, SchemeApplication
from ai_modules.scheme_finder import SchemeFinder

schemes_bp = Blueprint('schemes', __name__, url_prefix='/schemes')

@schemes_bp.route('/ai-recommend')
@login_required
def ai_recommend():
    """Fetch 5 AI-powered scheme recommendations and verify links."""
    finder = SchemeFinder()
    schemes = finder.get_recommendations(
        user_state=current_user.state, 
        user_district=current_user.district
    )
    
    # Verify links against local database
    verified_schemes = GovernmentScheme.query.all()
    
    for ai_s in schemes:
        ai_name = ai_s.get('name', '').upper()
        for db_s in verified_schemes:
            # Check if AI name matches DB name (fuzzy match)
            if db_s.name.upper() in ai_name or ai_name in db_s.name.upper():
                ai_s['link'] = db_s.apply_link
                # Also use DB description if it exists
                if db_s.description:
                    ai_s['description'] = db_s.description
                break
                
    return render_template('schemes/_ai_results.html', ai_schemes=schemes)

@schemes_bp.route('/')
def scheme_list():
    """View and search available government schemes."""
    q = request.args.get('q', '')
    category = request.args.get('category', 'all')
    
    query = GovernmentScheme.query
    
    if category and category != 'all':
        query = query.filter_by(category=category)
        
    if q:
        query = query.filter(GovernmentScheme.name.ilike(f'%{q}%'))
        
    schemes = query.order_by(GovernmentScheme.id.desc()).all()
    return render_template('schemes/schemes.html', schemes=schemes, search=q, category=category)

@schemes_bp.route('/apply/<int:scheme_id>', methods=['GET', 'POST'])
@login_required
def apply_scheme(scheme_id):
    """Handle direct applications for government schemes."""
    scheme = GovernmentScheme.query.get_or_404(scheme_id)
    
    if request.method == 'POST':
        applicant_name = request.form.get('applicant_name')
        aadhaar_number = request.form.get('aadhaar_number')
        contact_number = request.form.get('contact_number')
        address = request.form.get('address')
        
        try:
            # Create a new application
            application = SchemeApplication(
                user_id=current_user.id,
                scheme_id=scheme.id,
                applicant_name=applicant_name,
                aadhaar_number=aadhaar_number,
                contact_number=contact_number,
                address=address,
                status='Pending'
            )
            db.session.add(application)
            db.session.commit()
            
            flash(f'Successfully applied for {scheme.name}!', 'success')
            return redirect(url_for('schemes.scheme_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting application: {str(e)}', 'danger')
            return redirect(url_for('schemes.apply_scheme', scheme_id=scheme.id))
            
    return render_template('schemes/apply.html', scheme=scheme)
