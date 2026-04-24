import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from dotenv import load_dotenv

# Load explicitly here, but also handled in config.py
load_dotenv()

# Imports for initialization
from config import Config
from models import db
from models.user import User

# Import Blueprints
from routes.auth import auth_bp, bcrypt, mail
from routes.dashboard import dashboard_bp
from routes.chatbot import chatbot_bp
from routes.prediction import prediction_bp
from routes.recommendation import recommendation_bp
from routes.marketplace import marketplace_bp
from routes.schemes import schemes_bp
from routes.roadmap import roadmap_bp
from routes.fertilizer import fertilizer_bp
from routes.labour import labour_bp
from routes.shop import shop_bp
from routes.gov_mitra import gov_mitra_bp
from routes.education import education_bp
from routes.goat import goat_bp
from routes.cooler import cooler_bp
from routes.vision import vision_bp

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Database Initialization
    db.init_app(app)

    # Auth Initialization
    bcrypt.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Mail Initialization
    mail.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(marketplace_bp)
    app.register_blueprint(schemes_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(fertilizer_bp)
    app.register_blueprint(labour_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(gov_mitra_bp)
    app.register_blueprint(education_bp)
    app.register_blueprint(goat_bp)
    app.register_blueprint(cooler_bp)
    app.register_blueprint(vision_bp)

    # Ensure directories exist (Try/Except for Serverless read-only compatibility)
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(os.path.join(os.getcwd(), 'database'), exist_ok=True)
    except OSError:
        pass

    # Global Routes
    @app.route('/')
    def index():
        return render_template('index.html')
        
    @app.route('/health')
    def health():
        """Health check route for Render."""
        return "OK", 200

    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
        
    @app.errorhandler(500)
    def internal_error(e):
        return render_template('500.html'), 500

    return app

# Expose the app object globally for Gunicorn
app = create_app()

import threading

def seed_database(app_instance):
    """Background task to seed the database if it is empty."""
    with app_instance.app_context():
        from models.scheme import GovernmentScheme
        try:
            if GovernmentScheme.query.first() is None:
                print("Empty database detected. Auto-seeding famous schemes...")
                # Simplified list or import from separate script
                schemes = [
                    GovernmentScheme(
                        name="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
                        ministry="Ministry of Agriculture",
                        description="Financial assistance of ₹6,000 per year.",
                        benefits="₹6,000/year in 3 installments.",
                        eligibility="All landholding farmers.",
                        documents="Aadhaar, Land records, Bank details.",
                        apply_link="https://pmkisan.gov.in/",
                        category="Financial Support"
                    ),
                    GovernmentScheme(
                        name="E-Katha & Land Records (Karnataka)",
                        ministry="Revenue Dept, Karnataka",
                        description="Access digital records of land ownership.",
                        benefits="Digital RTC/Pani and Ownership verification.",
                        eligibility="Land owners in Karnataka.",
                        documents="Survey Number, Village details.",
                        apply_link="https://landrecords.karnataka.gov.in/",
                        category="Records",
                        is_state_specific=True,
                        state="Karnataka"
                    )
                ]
                db.session.bulk_save_objects(schemes)
                db.session.commit()
                print("Auto-seeding successful.")
        except Exception as e:
            print(f"Auto-seeding failed: {str(e)}")
            db.session.rollback()

    # Start seeding in background thread if needed
    # threading.Thread(target=seed_database, args=(app,)).start()

if __name__ == '__main__':
    with app.app_context():
        try:
            print("[DB Orbit] Establishing connection to BHOOMITRA Cloud (Supabase)...")
            from models.marketplace import CropListing
            from models.prediction import YieldPrediction, ChatHistory
            from models.scheme import GovernmentScheme, SchemeApplication
            from models.labour import LabourWorker
            from models.shop import Shop, Product, Supplier, Sale, SaleItem, AutoOrder, ShopNotification
            
            # Ensure all tables are created (including the new CustomerOrder table)
            db.create_all()
            print("[DB Orbit] Tables Synchronized.")
            
            # Migration: Sync Schema Columns (Resilient Mode)
            from sqlalchemy import text
            # 1. Product Image
            try:
                db.session.execute(text("ALTER TABLE shop_products ADD COLUMN IF NOT EXISTS image VARCHAR(255)"))
                db.session.commit()
            except: db.session.rollback()
            # 2. Partner Name
            try:
                db.session.execute(text("ALTER TABLE shops ADD COLUMN IF NOT EXISTS partner_name VARCHAR(150)"))
                db.session.commit()
            except: db.session.rollback()
            # 3. Partner Details
            try:
                db.session.execute(text("ALTER TABLE shops ADD COLUMN IF NOT EXISTS partner_details TEXT"))
                db.session.commit()
            except: db.session.rollback()
            # 4. Tracking ID
            try:
                db.session.execute(text("ALTER TABLE customer_orders ADD COLUMN IF NOT EXISTS tracking_id VARCHAR(50)"))
                db.session.commit()
            except: db.session.rollback()
            
            print("[DB Migration] Schema Sync: Processed.")
            
            # Skip create_all by default to prevent handshake hangs
            if os.getenv('SYNC_DB_ON_START', 'False') == 'True':
                db.create_all()
                print("[DB Orbit] Cloud Synchronization: ACTIVE.")
            else:
                print("[DB Orbit] Connection Synchronized Successfully.")
        except Exception as e:
            print(f"[DB Warning] Quick Sync Disturbance: {str(e)}")
            print("[DB Orbit] Continuing in Resilient Mode.")
    
    app.run(debug=True, port=5000)
