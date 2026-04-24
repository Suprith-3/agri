from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.crop import DiseaseDetection
from models.marketplace import CropListing
from models.prediction import PricePrediction, YieldPrediction, ChatHistory
from models.shop import Shop, CustomerOrder
import requests
from flask import current_app

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/sync-db')
@login_required
def sync_db():
    from sqlalchemy import text
    try:
        db.session.execute(text("ALTER TABLE shops ALTER COLUMN gst_number TYPE VARCHAR(50)"))
        db.session.commit()
        return "Database schema synchronized successfully! You can now register your shop."
    except Exception as e:
        db.session.rollback()
        return f"Sync error: {e}"

@dashboard_bp.route('/')
@login_required
def home():
    """Main farmer dashboard."""
    user_shop = Shop.query.filter_by(owner_id=current_user.id).first()
    # Statistics
    listings_count = CropListing.query.filter_by(farmer_id=current_user.id).count()
    price_preds = PricePrediction.query.filter_by(user_id=current_user.id).count()
    yield_preds = YieldPrediction.query.filter_by(user_id=current_user.id).count()
    total_preds = price_preds + yield_preds
    diseases_count = DiseaseDetection.query.filter_by(user_id=current_user.id).count()
    chats_count = ChatHistory.query.filter_by(user_id=current_user.id).count()
    
    # Recent Activity
    recent_diseases = DiseaseDetection.query.filter_by(user_id=current_user.id).order_by(DiseaseDetection.detected_at.desc()).limit(5).all()
    recent_prices = PricePrediction.query.filter_by(user_id=current_user.id).order_by(PricePrediction.created_at.desc()).limit(3).all()
    my_listings = CropListing.query.filter_by(farmer_id=current_user.id).order_by(CropListing.created_at.desc()).limit(3).all()

    # Crop Price Data (Last 7 Days)
    from datetime import datetime, timedelta
    import random
    
    end_date = datetime.utcnow()
    start_date = (end_date - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Realistic base prices for crops (₹/quintal)
    base_prices = {
        'ragi': 2850,
        'rice': 2100,
        'wheat': 2250
    }
    
    price_series = {
        'ragi': [],
        'rice': [],
        'wheat': []
    }
    labels = []
    
    for i in range(7):
        curr_day = (start_date + timedelta(days=i))
        labels.append(curr_day.strftime('%b %d'))
        
        for crop, base in base_prices.items():
            # Generate a realistic trend with slight daily variation
            daily_variation = (random.random() - 0.5) * 40 # +/- ₹20 variation
            price_series[crop].append(round(base + daily_variation, 2))

    # Weather (restored)
    weather_data = None
    if current_app.config.get('OPENWEATHER_API_KEY'):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={current_user.district},{current_user.state},IN&appid={current_app.config['OPENWEATHER_API_KEY']}&units=metric"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                w_json = r.json()
                weather_data = {
                    'temp': w_json['main']['temp'],
                    'humidity': w_json['main']['humidity'],
                    'condition': w_json['weather'][0]['main'],
                    'icon': w_json['weather'][0]['icon']
                }
        except:
            pass

    return render_template('dashboard/home.html', 
                           user=current_user,
                           stats={
                               'listings': listings_count,
                               'predictions': total_preds,
                               'diseases': diseases_count,
                               'chats': chats_count
                           },
                           price_labels=labels,
                           price_series=price_series,
                           recent_diseases=recent_diseases,
                           recent_prices=recent_prices,
                           my_listings=my_listings,
                           weather_data=weather_data,
                           user_shop=user_shop)

@dashboard_bp.route('/my-orders')
@login_required
def my_orders():
    """User's purchase history and status."""
    orders = CustomerOrder.query.filter_by(user_id=current_user.id).order_by(CustomerOrder.created_at.desc()).all()
    return render_template('dashboard/my_orders.html', orders=orders)
