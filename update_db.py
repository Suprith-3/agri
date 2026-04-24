import os
from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

print("Updating database schema...")
with app.app_context():
    try:
        # Check if we are using SQLite or PostgreSQL
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        is_sqlite = db_uri.startswith('sqlite')

        if is_sqlite:
            print("Detected SQLite Database. Adding columns if missing...")
            # SQLite doesn't support 'ADD COLUMN IF NOT EXISTS' directly in one statement easily
            # We'll try to add them and catch errors if they already exist
            cols_to_add = [
                ("shops", "partner_name", "VARCHAR(150)"),
                ("shops", "partner_details", "TEXT"),
                ("customer_orders", "tracking_id", "VARCHAR(50)")
            ]
            for table, col, col_type in cols_to_add:
                try:
                    db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                    db.session.commit()
                    print(f"Added {col} to {table}")
                except Exception as e:
                    db.session.rollback()
                    if 'duplicate column name' in str(e).lower():
                        print(f"Column {col} already exists in {table}, skipping.")
                    else:
                        print(f"Error adding {col} to {table}: {e}")
        else:
            print("Detected PostgreSQL/Cloud Database. Running ALTER TABLE...")
            db.session.execute(text("ALTER TABLE shops ADD COLUMN IF NOT EXISTS partner_name VARCHAR(150)"))
            db.session.execute(text("ALTER TABLE shops ADD COLUMN IF NOT EXISTS partner_details TEXT"))
            db.session.execute(text("ALTER TABLE customer_orders ADD COLUMN IF NOT EXISTS tracking_id VARCHAR(50)"))
            db.session.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_tracking_id ON customer_orders (tracking_id) WHERE tracking_id IS NOT NULL"))
            db.session.commit()
            print("PostgreSQL Database updated successfully!")

        print("\nSUCCESS: Database updated with Partner and Tracking features!")
    except Exception as e:
        db.session.rollback()
        print(f"\nCRITICAL ERROR: {e}")
        print("Please contact support if this error persists.")
