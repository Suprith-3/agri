from app import create_app
from models import db
from models.goat import GoatExpert

app = create_app()

def seed_goats():
    with app.app_context():
        # Clear existing (Delete Unlocks first to avoid foreign key errors)
        from models.goat import GoatUnlock
        print("[Seed] Clearing previous data...")
        GoatUnlock.query.delete()
        GoatExpert.query.delete()
        db.session.commit()
        
        experts = [
            ("M. S. Swaminathan", "Father of Green Revolution", "Developed high-yielding varieties of wheat and rice.", "Green Revolution", "https://images.unsplash.com/photo-1595152772835-219674b2a8a6?q=80&w=400", "Mon 10:00 AM"),
            ("Verghese Kurien", "Father of White Revolution", "The brain behind Amul and the world's largest dairy development program.", "Dairy Farming", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=400", "Tue 2:00 PM"),
            ("Subhash Palekar", "Zero Budget Natural Farming (ZBNF)", "Pioneered chemical-free agriculture using local resources.", "Natural Farming", "https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=400", "Wed 6:00 PM"),
            ("Rahibai Popere", "Seed Mother of India", "Founder of the indigenous seed bank for tribal farmers.", "Seed Conservation", "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?q=80&w=400", "Thu 11:00 AM"),
            ("Chintala Venkat Reddy", "Innovation Pioneer", "First individual farmer to receive a patent for soil restoration.", "Soil Health", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?q=80&w=400", "Fri 4:00 PM"),
            ("Sivakumar Palaniappan", "Smart Farming Guru", "Integrating IoT and AI into traditional Tamil Nadu farming.", "Precision Agri", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=400", "Sat 9:00 AM"),
            ("Dr. Atmaram Pandey", "Soil Scientist", "Global expert on organic carbon and micronutrient management.", "Bio-Fertilizers", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?q=80&w=400", "Sun 5:00 PM"),
            ("Kushal Pal Singh", "Sugarcane Legend", "Revolutionized high-density planting for sugarcane in UP.", "Commercial Crops", "https://images.unsplash.com/photo-1552058544-f2b08422138a?q=80&w=400", "Mon 11:00 AM"),
            ("Shyama Prasad", "Hydroponics Master", "The leader of urban terrace farming and soil-less agriculture.", "Hydroponics", "https://images.unsplash.com/photo-1517841905240-472988babdf9?q=80&w=400", "Tue 6:00 PM"),
            ("G. Nammalvar", "Organic Icon", "The man who spent his life teaching farmers to reject pesticides.", "Organic Farming", "https://images.unsplash.com/photo-1441786917082-5a24a00c718c?q=80&w=400", "Wed 10:00 AM"),
            ("Dr. G.V. Ramanjaneyulu", "Agri Policy Expert", "Advocate for sustainable livelihoods and farmer rights.", "Agri Economics", "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?q=80&w=400", "Thu 3:00 PM"),
            ("Nirmal Singh", "Drip Irrigation Pro", "Successfully implemented drip systems in the driest parts of Punjab.", "Water Mgmt", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=400", "Fri 8:00 AM"),
            ("Aruna Roy", "Social Agri Activist", "Empowering rural women through grain banks and small cooperatives.", "Social Forestry", "https://images.unsplash.com/photo-1567532939604-b6c5b0ad2e01?q=80&w=400", "Sat 2:00 PM"),
            ("Dr. K.P. Prabhakaran", "Coconut Guru", "Developer of the most pest-resistant coconut hybrids in Kerala.", "Plant Breeding", "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=400", "Sun 10:00 AM"),
            ("Manish Singh", "Vertical Farming Expert", "Leading the future of high-tech vertical farms in India.", "Vertical Agri", "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?q=80&w=400", "Mon 4:00 PM"),
            ("Dr. S. Ayyappan", "Aquaculture Specialist", "Former ICAR DG and world-renowned fisheries scientist.", "Fisheries", "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?q=80&w=400", "Tue 10:00 AM"),
            ("T. Pradeep", "Nano-Technology in Agri", "Applying nanotechnology for clean water and smart fertilizers.", "Nano Agri", "https://images.unsplash.com/photo-1537368910025-700350fe46c7?q=80&w=400", "Wed 3:00 PM"),
            ("Rajendra Singh", "Waterman of India", "Known for reviving traditional water harvesting methods (Johads).", "Water Harvesting", "https://images.unsplash.com/photo-1504257432389-52343af06ae3?q=80&w=400", "Thu 7:00 PM"),
            ("Dr. Sanjay Rajaram", "World Food Prize Winner", "Bred over 480 varieties of wheat used globally.", "Wheat Research", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=400", "Fri 11:00 AM"),
            ("Shobhana Kumar", "Permaculture Designer", "Teaching farmers how to create self-sustaining forest gardens.", "Permaculture", "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?q=80&w=400", "Sat 5:00 PM")
        ]

        for name, title, desc, spec, img, sched in experts:
            expert = GoatExpert(name=name, title=title, description=desc, specialty=spec, image_url=img, schedule_time=sched)
            db.session.add(expert)
        
        db.session.commit()
        print("Successfully Seeded 20 GOAT Agricultural Legends!")

if __name__ == "__main__":
    seed_goats()
