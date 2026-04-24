from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        print("[DB Orbit] Synchronizing Supabase Schema...")
        # Alter the column length in PostgreSQL
        db.session.execute(text("ALTER TABLE shops ALTER COLUMN gst_number TYPE VARCHAR(50)"))
        db.session.commit()
        print("[DB Orbit] Column 'gst_number' expanded successfully in BHOOMITRA Cloud.")
    except Exception as e:
        print(f"[DB Orbit] Sync Error: {e}")
        db.session.rollback()
