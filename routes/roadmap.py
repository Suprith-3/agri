from flask import Blueprint, render_template, request, flash, current_app
from flask_login import login_required, current_user
from ai_modules.roadmap_generator import RoadmapGenerator

roadmap_bp = Blueprint('roadmap', __name__, url_prefix='/roadmap')

@roadmap_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Handle the farming roadmap generation page."""
    roadmap_data = None
    if request.method == 'POST':
        crop = request.form.get('crop')
        soil = request.form.get('soil')
        water = request.form.get('water')
        location = request.form.get('location') or f"{current_user.district}, {current_user.state}"
        
        if not crop or not soil or not water:
            flash('Please fill in all required fields.', 'warning')
        else:
            try:
                api_key = current_app.config.get('OPENROUTER_API_KEY')
                generator = RoadmapGenerator(api_key=api_key)
                roadmap_data = generator.generate_roadmap(crop, soil, water, location)
                flash('Farming roadmap generated successfully!', 'success')
            except Exception as e:
                flash(f'Error generating roadmap: {str(e)}', 'danger')

    return render_template('roadmap/index.html', roadmap_data=roadmap_data)
