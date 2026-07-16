import os
import sys

# Add root folder to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import SessionLocal, Base, engine
from backend.app.models import User, Supplier, FreightHistory, PredictionHistory, Recommendation
from backend.app.services.auth import AuthService
import datetime

def seed_database():
    print("Starting database seeding...")
    db = SessionLocal()
    
    try:
        # 1. Clear existing data if any (optional, but good for resetting)
        # We can drop and recreate tables to ensure clean seeding
        print("Recreating database tables...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        # 2. Add Default User
        print("Creating default admin account...")
        admin_pass_hash = AuthService.hash_password("password123")
        admin_user = User(username="admin", password_hash=admin_pass_hash)
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Admin user created (Username: admin, Password: password123)")
        
        # 3. Add Mock Suppliers (12 suppliers with realistic details)
        print("Seeding suppliers...")
        suppliers_data = [
            # Product: Lithium-Ion Batteries
            {
                "name": "Tata AutoComp Systems",
                "country": "India",
                "product_name": "Lithium-Ion Batteries",
                "product_cost": 450000.00,
                "delivery_time": 4,
                "quality_rating": 4.8,
                "late_deliveries": 1,
                "experience": 8,
                "contact_info": "pune.sales@tataautocomp.com | +91 20 6608 5000"
            },
            {
                "name": "Exide Industries Ltd",
                "country": "India",
                "product_name": "Lithium-Ion Batteries",
                "product_cost": 420000.00,
                "delivery_time": 6,
                "quality_rating": 4.2,
                "late_deliveries": 3,
                "experience": 12,
                "contact_info": "corp@exide.co.in | +91 33 2284 3130"
            },
            {
                "name": "CATL Technology Co.",
                "country": "China",
                "product_name": "Lithium-Ion Batteries",
                "product_cost": 390000.00,
                "delivery_time": 18,
                "quality_rating": 4.6,
                "late_deliveries": 8,
                "experience": 10,
                "contact_info": "global.sales@catl.com | +86 593 258 3666"
            },
            
            # Product: Active Pharmaceutical Ingredients (API)
            {
                "name": "Dr. Reddy's Laboratories",
                "country": "India",
                "product_name": "API - Paracetamol",
                "product_cost": 150000.00,
                "delivery_time": 3,
                "quality_rating": 4.7,
                "late_deliveries": 0,
                "experience": 15,
                "contact_info": "api.sales@drreddys.com | +91 40 4900 2900"
            },
            {
                "name": "Aurobindo Pharma",
                "country": "India",
                "product_name": "API - Paracetamol",
                "product_cost": 135000.00,
                "delivery_time": 5,
                "quality_rating": 4.3,
                "late_deliveries": 4,
                "experience": 11,
                "contact_info": "info@aurobindo.com | +91 40 6672 5000"
            },
            {
                "name": "Sinopharm Chemicals",
                "country": "China",
                "product_name": "API - Paracetamol",
                "product_cost": 120000.00,
                "delivery_time": 22,
                "quality_rating": 3.9,
                "late_deliveries": 12,
                "experience": 7,
                "contact_info": "export@sinopharm.com | +86 10 8440 7666"
            },

            # Product: Solar PV Panels
            {
                "name": "Waaree Energies Ltd",
                "country": "India",
                "product_name": "Solar PV Panels",
                "product_cost": 280000.00,
                "delivery_time": 5,
                "quality_rating": 4.6,
                "late_deliveries": 2,
                "experience": 9,
                "contact_info": "sales@waaree.com | 1800 2121 321"
            },
            {
                "name": "Adani Solar",
                "country": "India",
                "product_name": "Solar PV Panels",
                "product_cost": 295000.00,
                "delivery_time": 4,
                "quality_rating": 4.7,
                "late_deliveries": 1,
                "experience": 6,
                "contact_info": "solar.sales@adani.com | +91 79 2555 5555"
            },
            {
                "name": "Longi Green Energy",
                "country": "China",
                "product_name": "Solar PV Panels",
                "product_cost": 240000.00,
                "delivery_time": 25,
                "quality_rating": 4.5,
                "late_deliveries": 14,
                "experience": 13,
                "contact_info": "en@longi.com | +86 29 8156 6666"
            },

            # Product: Specialty Steel Alloys
            {
                "name": "Jindal Stainless Steel",
                "country": "India",
                "product_name": "Specialty Steel Alloys",
                "product_cost": 75000.00,
                "delivery_time": 3,
                "quality_rating": 4.5,
                "late_deliveries": 2,
                "experience": 20,
                "contact_info": "steel.sales@jindal.com | +91 11 2618 8345"
            },
            {
                "name": "Tata Steel Europe",
                "country": "Germany",
                "product_name": "Specialty Steel Alloys",
                "product_cost": 95000.00,
                "delivery_time": 14,
                "quality_rating": 4.9,
                "late_deliveries": 1,
                "experience": 25,
                "contact_info": "europe@tatasteel.com | +49 211 4924 0"
            },
            {
                "name": "Nippon Steel Corp",
                "country": "Japan",
                "product_name": "Specialty Steel Alloys",
                "product_cost": 110000.00,
                "delivery_time": 18,
                "quality_rating": 4.95,
                "late_deliveries": 0,
                "experience": 30,
                "contact_info": "info@nipponsteel.com | +81 3 6867 4111"
            }
        ]
        
        for s_info in suppliers_data:
            supplier = Supplier(**s_info)
            db.add(supplier)
        
        db.commit()
        print("Suppliers seeded successfully.")
        
        # 4. Seed Freight History (Historical records)
        print("Seeding historical freight runs...")
        freight_runs = [
            {"origin": "Mumbai", "destination": "Pune", "distance": 150.0, "fuel_price": 95.50, "month": "January", "freight_cost": 4125.00},
            {"origin": "Mumbai", "destination": "Nashik", "distance": 170.0, "fuel_price": 96.00, "month": "February", "freight_cost": 4480.00},
            {"origin": "Mumbai", "destination": "Nagpur", "distance": 800.0, "fuel_price": 98.20, "month": "July", "freight_cost": 16420.00},
            {"origin": "Pune", "destination": "Nagpur", "distance": 710.0, "fuel_price": 97.40, "month": "August", "freight_cost": 14950.00},
            {"origin": "Nashik", "destination": "Aurangabad", "distance": 190.0, "fuel_price": 95.80, "month": "October", "freight_cost": 5350.00},
            {"origin": "Kolhapur", "destination": "Mumbai", "distance": 380.0, "fuel_price": 94.90, "month": "May", "freight_cost": 7210.00},
            {"origin": "Nagpur", "destination": "Aurangabad", "distance": 480.0, "fuel_price": 99.10, "month": "November", "freight_cost": 10520.00}
        ]
        
        for fr in freight_runs:
            hist = FreightHistory(
                origin=fr["origin"],
                destination=fr["destination"],
                distance=fr["distance"],
                fuel_price=fr["fuel_price"],
                month=fr["month"],
                freight_cost=fr["freight_cost"]
            )
            db.add(hist)
            
        db.commit()
        print("Historical freight data seeded.")

        # 5. Add a couple of initial prediction runs
        print("Seeding initial prediction runs...")
        pred1 = PredictionHistory(
            user_id=admin_user.id,
            origin="Mumbai",
            destination="Pune",
            distance=150.0,
            fuel_price=95.50,
            month="January",
            predicted_freight_cost=4250.00,
            confidence_score=95.46
        )
        pred2 = PredictionHistory(
            user_id=admin_user.id,
            origin="Mumbai",
            destination="Nagpur",
            distance=800.0,
            fuel_price=98.00,
            month="July",
            predicted_freight_cost=16580.00,
            confidence_score=95.46
        )
        db.add(pred1)
        db.add(pred2)
        db.commit()
        
        # 6. Seed a recommendation
        print("Seeding initial recommendation record...")
        # Rec for lithium-ion batteries
        # tata autocomp id is 1, pred1 id is 1
        rec = Recommendation(
            user_id=admin_user.id,
            prediction_id=pred1.id,
            recommended_supplier_id=1,
            total_landed_cost=454298.00, # product_cost=450000, freight=4250.00, premium=48.00 (Tata is low risk)
            product_cost=450000.00,
            predicted_freight_cost=4250.00,
            risk_premium=48.00
        )
        db.add(rec)
        db.commit()
        print("Database seeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
