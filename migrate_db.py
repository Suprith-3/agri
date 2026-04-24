from app import app, db
import os

# Import all models to ensure they are registered with SQLAlchemy
from models.user import User
from models.crop import DiseaseDetection
from models.marketplace import CropListing
from models.prediction import PricePrediction, YieldPrediction, ChatHistory
from models.scheme import GovernmentScheme, SchemeApplication
from models.labour import LabourWorker
from models.shop import Shop, Product, Supplier, Sale, SaleItem, AutoOrder, ShopNotification
from models.gov_mitra import QuarterlySurvey
from models.education import Course, Lesson
from models.rental import UserVerification, RentalItem, RentalBooking

def run_migration():
    """Creates all tables in the Supabase database defined in .env"""
    with app.app_context():
        print("--------------------------------------------------")
        print("[DB Orbit] Connecting to BHOOMITRA Cloud (Supabase)...")
        try:
            # This creates all tables defined in models/
            db.create_all()
            print("[DB Orbit] Success: All tables created/verified.")
            print("--------------------------------------------------")
        except Exception as e:
            print(f"[DB Error] Migration failed: {str(e)}")
            print("--------------------------------------------------")

if __name__ == '__main__':
    run_migration()
