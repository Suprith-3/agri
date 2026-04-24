from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from models import db
from models.prediction import PricePrediction, YieldPrediction, MarketRate
from ai_modules.price_predictor import PricePredictor
from ai_modules.yield_predictor import YieldPredictor
from ai_modules.market_fetcher import MarketFetcher
from datetime import datetime

prediction_bp = Blueprint('prediction', __name__, url_prefix='/prediction')

@prediction_bp.route('/price', methods=['GET', 'POST'])
@login_required
def price():
    """Handle crop price prediction."""
    if request.method == 'POST':
        crop = request.form.get('crop')
        state = request.form.get('state')
        month = int(request.form.get('month'))
        year = int(request.form.get('year'))
        season = request.form.get('season')
        market_type = request.form.get('market_type')
        
        try:
            prediction_api = current_app.config.get('OPENROUTER_API_KEY')
            predictor = PricePredictor(gemini_api_key=prediction_api)
            predicted_price = predictor.predict(crop, state, month, year, season, market_type)
            
            # Save to history
            record = PricePrediction(
                user_id=current_user.id,
                crop=crop,
                state=state,
                month=month,
                year=year,
                predicted_price=predicted_price
            )
            db.session.add(record)
            db.session.commit()
            
            flash('Prediction successful!', 'success')
            
            # Pass data back to template for rendering charts
            return render_template('prediction/price.html', 
                                   result={
                                       'predicted_price': predicted_price,
                                       'crop': crop,
                                       'month': month,
                                       'year': year,
                                       'range_low': predicted_price * 0.9,
                                       'range_high': predicted_price * 1.1
                                   })
        except Exception as e:
            db.session.rollback()
            flash(f'Error predicting price: {str(e)}', 'danger')
            return redirect(url_for('prediction.price'))
            
    return render_template('prediction/price.html', result=None)

@prediction_bp.route('/yield', methods=['GET', 'POST'])
@login_required
def yield_prediction():
    """Handle crop yield and profit estimation using Gemini AI."""
    if request.method == 'POST':
        crop = request.form.get('crop')
        area = float(request.form.get('area', 1))
        soil_type = request.form.get('soil_type')
        irrigation = request.form.get('irrigation')
        
        try:
            predictor = YieldPredictor()
            # Fetch user location
            state = current_user.state or "Karnataka"
            district = current_user.district or "Unknown"
            
            data = predictor.predict(crop, area, state, district, soil_type, irrigation)
            
            # Additional tips
            tips = predictor.get_improvement_suggestions(crop, soil_type, irrigation)
            
            record = YieldPrediction(
                user_id=current_user.id,
                crop=crop,
                area=area,
                soil_type=soil_type,
                irrigation=irrigation,
                predicted_yield=data.get('total_yield', 0),
                estimated_revenue=data.get('total_revenue', 0)
            )
            db.session.add(record)
            db.session.commit()
            
            # Safely round the results for UI display
            formatted_result = {
                'total_yield': round(float(data.get('total_yield') or 0), 2),
                'yield_per_acre': round(float(data.get('yield_per_acre') or 0), 2),
                'est_revenue': round(float(data.get('total_revenue') or 0), 0),
                'est_profit': round(float(data.get('estimated_profit') or 0), 0),
                'est_cost': round(float(data.get('cost_of_cultivation') or 0), 0),
                'market_price': round(float(data.get('estimated_market_price') or 0), 0),
                'confidence': data.get('confidence_score', '80%'),
                'tips': tips,
                'crop': crop,
                'location': f"{district}, {state}"
            }
            
            flash('Yield and Profit estimation completed!', 'success')
            return render_template('prediction/yield.html', result=formatted_result)
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error predicting yield: {str(e)}', 'danger')
            return redirect(url_for('prediction.yield_prediction'))
            
    return render_template('prediction/yield.html', result=None)

@prediction_bp.route('/live')
@login_required
def live_rates():
    """Display real-time APMC market rates."""
    search_query = request.args.get('search')
    
    # If searching specifically, always fetch fresh from AI
    if search_query:
        try:
            api_key = current_app.config.get('OPENROUTER_API_KEY')
            fetcher = MarketFetcher(api_key=api_key)
            raw_rates = fetcher.fetch_latest_rates(state=current_user.state or "Karnataka", crop=search_query)
            
            if raw_rates:
                # Add a timestamp to raw results for the template
                now = datetime.utcnow()
                for r in raw_rates:
                    r['last_updated'] = now
                    # Ensure price is a number for formatting
                    r['price'] = float(r.get('price') or 0)
                
                return render_template('prediction/market_rates.html', rates=raw_rates)
        except Exception as e:
            print(f"Search error: {e}")

    # Standard periodic update logic
    latest_record = MarketRate.query.order_by(MarketRate.last_updated.desc()).first()
    
    needs_update = False
    if not latest_record:
        needs_update = True
    else:
        diff = datetime.utcnow() - latest_record.last_updated
        if diff.total_seconds() > 3600: # 1 hour
            needs_update = True
            
    if needs_update:
        try:
            api_key = current_app.config.get('OPENROUTER_API_KEY')
            fetcher = MarketFetcher(api_key=api_key)
            rates = fetcher.fetch_latest_rates(state=current_user.state or "Karnataka")
            
            if rates:
                # Clear old rates or just update? Clear for fresh 'live' feel
                MarketRate.query.delete()
                for r in rates:
                    new_rate = MarketRate(
                        crop=r.get('crop'),
                        state=r.get('state'),
                        mandi=r.get('mandi'),
                        price=float(r.get('price') or 0),
                        arrival_quantity=r.get('arrival_quantity')
                    )
                    db.session.add(new_rate)
                db.session.commit()
        except Exception as e:
            print(f"Update error: {e}")

    all_rates = MarketRate.query.order_by(MarketRate.crop).all()
    return render_template('prediction/market_rates.html', rates=all_rates)
