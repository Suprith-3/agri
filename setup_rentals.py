from app import create_app
from models import db
from models.rental import RentalItem
from models.user import User

app = create_app()

with app.app_context():
    print("[Rental] Creating tables...")
    db.create_all()
    
    # Check if a sample tractor already exists
    existing = RentalItem.query.filter_by(name='Mahindra 575 DI Tractor').first()
    if not existing:
        # Get first user as owner
        owner = User.query.first()
        if owner:
            print("[Rental] Adding sample tractor...")
            r = RentalItem(
                name='Mahindra 575 DI Tractor', 
                description='High-performance tractor, excellent condition. Includes plow and tiller attachments.', 
                category='Machinery', 
                hourly_rate=500.0, 
                daily_rate=2500.0, 
                image_url='https://images.unsplash.com/photo-1594498257602-0175c0f9461f?q=80&w=400', 
                owner_id=owner.id
            )
            db.session.add(r)
            db.session.commit()
            print("[Rental] Success: Sample machinery added!")
        else:
            print("[Rental] Error: No users found in database to assign as owner.")
    else:
        print("[Rental] Sample machinery already exists.")

    print("--------------------------------------------------")
    print("Agri-Rent Hub is now LIVE!")
    print("--------------------------------------------------")
