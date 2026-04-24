from flask import Blueprint, render_template, request, flash, current_app
from flask_login import login_required, current_user
from ai_modules.crop_recommender import CropRecommender

recommendation_bp = Blueprint('recommendation', __name__, url_prefix='/recommendation')

@recommendation_bp.route('/map', methods=['GET', 'POST'])
@login_required
def recommend_map():
    """Handle interactive location-based crop recommendation."""
    if request.method == 'POST':
        lat = float(request.form.get('lat', 20.5937)) # Default India
        lng = float(request.form.get('lng', 78.9629))
        soil_type = request.form.get('soil_type')
        water = request.form.get('water')
        sz = request.form.get('farm_size')
        budget = request.form.get('budget')
        season = request.form.get('season')
        
        try:
            weather_api = current_app.config.get('OPENWEATHER_API_KEY')
            openrouter_api = current_app.config.get('OPENROUTER_API_KEY')
            recommender = CropRecommender(weather_api_key=weather_api, gemini_api_key=openrouter_api)
            recommendations = recommender.recommend(soil_type, water, season, lat, lng)
            
            # Enrich with weather if available
            weather = recommender.get_weather(lat, lng)
            
            flash('Recommendations generated successfully!', 'success')
            return render_template('recommendation/map.html', 
                                   recommendations=recommendations,
                                   weather=weather,
                                   lat=lat, lng=lng)
        except Exception as e:
            flash(f'Error generating recommendations: {str(e)}', 'danger')

    return render_template('recommendation/map.html')
