from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.gov_mitra import QuarterlySurvey
from datetime import datetime

gov_mitra_bp = Blueprint('gov_mitra', __name__, url_prefix='/gov-mitra')

@gov_mitra_bp.route('/')
@login_required
def dashboard():
    """Official dashboard for government surveying."""
    # Fetch farmers and recent surveys
    farmers = User.query.filter_by(role='farmer').all()
    recent_surveys = QuarterlySurvey.query.order_by(QuarterlySurvey.created_at.desc()).limit(15).all()
    
    return render_template('gov_mitra/dashboard.html', 
                           farmers=farmers, 
                           recent_surveys=recent_surveys)

@gov_mitra_bp.route('/survey/new', methods=['GET', 'POST'])
@login_required
def new_survey():
    if request.method == 'POST':
        farmer_id = request.form.get('farmer_id')
        quarter = int(request.form.get('quarter'))
        year = int(request.form.get('year'))
        crop = request.form.get('crop_grown')
        revenue = float(request.form.get('revenue', 0))
        expenses = float(request.form.get('expenses', 0))
        
        new_entry = QuarterlySurvey(
            user_id=farmer_id,
            quarter=quarter,
            year=year,
            crop_grown=crop,
            revenue=revenue,
            expenses=expenses,
            profit_loss=revenue - expenses,
            face_scan_verified=True if request.form.get('face_scan') else False,
            collecting_official=current_user.name,
            notes=request.form.get('notes')
        )
        
        db.session.add(new_entry)
        db.session.commit()
        flash(f'Quarter {quarter} report for Farmer ID {farmer_id} logged successfully.', 'success')
        return redirect(url_for('gov_mitra.dashboard'))
        
    farmers = User.query.filter_by(role='farmer').all()
    current_year = datetime.now().year
    return render_template('gov_mitra/survey_form.html', farmers=farmers, current_year=current_year)

@gov_mitra_bp.route('/farmer-history/<int:farmer_id>')
@login_required
def farmer_history(farmer_id):
    farmer = User.query.get_or_404(farmer_id)
    surveys = QuarterlySurvey.query.filter_by(user_id=farmer_id).order_by(QuarterlySurvey.year.desc(), QuarterlySurvey.quarter.desc()).all()
    
    # --- AI Advanced Analysis (Nearby Land Comparison) ---
    suggestion = "Stay with current crop cycle."
    yearly_profit = sum(s.profit_loss for s in surveys if s.year == datetime.now().year)
    
    # 1. Look for top-performing crops in the SAME DISTRICT
    nearby_top_crop = db.session.query(QuarterlySurvey.crop_grown)\
        .join(User, User.id == QuarterlySurvey.user_id)\
        .filter(User.district == farmer.district)\
        .filter(QuarterlySurvey.profit_loss > 0)\
        .order_by(QuarterlySurvey.profit_loss.desc())\
        .first()

    if nearby_top_crop:
        top_crop_name = nearby_top_crop[0]
        if yearly_profit < 0:
            suggestion = f"Recommendation: Your land is currently underperforming. Nearby farms in {farmer.district} are finding high success with '{top_crop_name}'. Switch to this for better stability."
        elif yearly_profit > 100000:
            suggestion = f"Recommendation: Excellent performance. While you are doing well, nearby elite farms are also leveraging '{top_crop_name}'. Consider a hybrid plantation for maximized yield."
    elif yearly_profit < 0:
        suggestion = "Recommendation: Performance is low. No local high-yield data found yet. Suggest testing drought-resistant millets."

    return render_template('gov_mitra/farmer_detail.html', 
                           farmer=farmer, 
                           surveys=surveys, 
                           suggestion=suggestion,
                           yearly_profit=yearly_profit)
