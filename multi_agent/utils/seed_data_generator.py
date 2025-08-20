"""
Seed data generator for retail returns and warranty data.
Generates realistic data for the last 90 days with seasonal patterns.
"""

import random
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from faker import Faker
from sqlalchemy.orm import Session

from multi_agent.models.database_models import Product, Return, Warranty
from multi_agent.config.database import db_manager

fake = Faker()

class SeedDataGenerator:
    """Generate realistic seed data for testing and development."""
    
    def __init__(self):
        self.products_data = self._get_product_catalog()
        self.return_reasons = [
            "Defective product", "Wrong size", "Wrong color", "Not as described",
            "Quality issues", "Damaged in shipping", "Changed mind", "Price match",
            "Better price elsewhere", "Warranty claim", "Technical issues"
        ]
        self.warranty_issues = [
            "Screen defect", "Battery failure", "Charging issues", "Software bugs",
            "Hardware malfunction", "Performance degradation", "Connectivity problems",
            "Physical damage", "Overheating", "Audio problems", "Display issues"
        ]
        self.store_locations = [
            "New York - Manhattan", "Los Angeles - Beverly Hills", "Chicago - Downtown",
            "Houston - Galleria", "Phoenix - Scottsdale", "Philadelphia - Center City",
            "San Antonio - Riverwalk", "San Diego - Mission Valley", "Dallas - Uptown",
            "San Jose - Valley Fair", "Austin - Domain", "Jacksonville - Town Center"
        ]
        self.statuses = ["Resolved", "Pending", "In Progress", "Escalated", "Closed"]
    
    def _get_product_catalog(self) -> List[Dict[str, Any]]:
        """Define product catalog with realistic data."""
        return [
            # Electronics
            {"id": "ELEC001", "name": "Smartphone Pro X", "category": "Electronics", "price": 999.99, "brand": "TechCorp"},
            {"id": "ELEC002", "name": "Laptop Ultra 15", "category": "Electronics", "price": 1299.99, "brand": "CompuTech"},
            {"id": "ELEC003", "name": "Wireless Headphones", "category": "Electronics", "price": 199.99, "brand": "AudioMax"},
            {"id": "ELEC004", "name": "Smart Watch Series 5", "category": "Electronics", "price": 399.99, "brand": "WearTech"},
            {"id": "ELEC005", "name": "Tablet Air 11", "category": "Electronics", "price": 599.99, "brand": "TabletCo"},
            
            # Clothing
            {"id": "CLTH001", "name": "Premium Denim Jeans", "category": "Clothing", "price": 89.99, "brand": "DenimCraft"},
            {"id": "CLTH002", "name": "Cotton T-Shirt Pack", "category": "Clothing", "price": 29.99, "brand": "BasicWear"},
            {"id": "CLTH003", "name": "Winter Jacket", "category": "Clothing", "price": 159.99, "brand": "OutdoorGear"},
            {"id": "CLTH004", "name": "Running Shoes", "category": "Clothing", "price": 129.99, "brand": "SportMax"},
            {"id": "CLTH005", "name": "Business Suit", "category": "Clothing", "price": 299.99, "brand": "FormalWear"},
            
            # Home & Garden
            {"id": "HOME001", "name": "Coffee Maker Deluxe", "category": "Home & Garden", "price": 79.99, "brand": "BrewMaster"},
            {"id": "HOME002", "name": "Vacuum Cleaner Pro", "category": "Home & Garden", "price": 199.99, "brand": "CleanTech"},
            {"id": "HOME003", "name": "Garden Tool Set", "category": "Home & Garden", "price": 49.99, "brand": "GreenThumb"},
            {"id": "HOME004", "name": "LED Desk Lamp", "category": "Home & Garden", "price": 39.99, "brand": "LightCraft"},
            {"id": "HOME005", "name": "Kitchen Knife Set", "category": "Home & Garden", "price": 89.99, "brand": "ChefPro"},
            
            # Sports & Outdoors
            {"id": "SPRT001", "name": "Yoga Mat Premium", "category": "Sports & Outdoors", "price": 29.99, "brand": "YogaLife"},
            {"id": "SPRT002", "name": "Camping Tent 4-Person", "category": "Sports & Outdoors", "price": 199.99, "brand": "CampGear"},
            {"id": "SPRT003", "name": "Mountain Bike", "category": "Sports & Outdoors", "price": 599.99, "brand": "BikeMax"},
            {"id": "SPRT004", "name": "Fishing Rod Kit", "category": "Sports & Outdoors", "price": 79.99, "brand": "AnglePro"},
            {"id": "SPRT005", "name": "Basketball Official", "category": "Sports & Outdoors", "price": 24.99, "brand": "SportBall"},
            
            # Beauty & Health
            {"id": "HLTH001", "name": "Skincare Set Premium", "category": "Beauty & Health", "price": 149.99, "brand": "GlowCare"},
            {"id": "HLTH002", "name": "Electric Toothbrush", "category": "Beauty & Health", "price": 89.99, "brand": "DentalTech"},
            {"id": "HLTH003", "name": "Hair Dryer Professional", "category": "Beauty & Health", "price": 79.99, "brand": "StylePro"},
            {"id": "HLTH004", "name": "Vitamin Supplement Pack", "category": "Beauty & Health", "price": 39.99, "brand": "HealthMax"},
            {"id": "HLTH005", "name": "Massage Gun", "category": "Beauty & Health", "price": 199.99, "brand": "RecoveryTech"}
        ]
    
    def generate_products(self, session: Session) -> List[Product]:
        """Generate and insert product catalog."""
        products = []
        for product_data in self.products_data:
            product = Product(**product_data)
            products.append(product)
            session.add(product)
        
        session.commit()
        print(f"Generated {len(products)} products")
        return products
    
    def generate_returns(self, session: Session, num_returns: int = 1000) -> List[Return]:
        """Generate realistic return records for the last 90 days."""
        returns = []
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        
        # Get all product IDs
        product_ids = [p["id"] for p in self.products_data]
        
        for _ in range(num_returns):
            # Generate random date in the last 90 days
            random_days = random.randint(0, 90)
            return_date = end_date - timedelta(days=random_days)
            
            # Select random product with category bias (electronics have more returns)
            product = random.choice(self.products_data)
            if product["category"] == "Electronics":
                # Electronics have higher return probability
                if random.random() > 0.7:  # 30% chance to skip
                    continue
            
            return_record = Return(
                order_id=f"ORD-{fake.uuid4()[:8].upper()}",
                product_id=product["id"],
                return_date=return_date,
                reason=random.choice(self.return_reasons),
                resolution_status=random.choice(self.statuses),
                store_location=random.choice(self.store_locations),
                customer_id=f"CUST-{fake.uuid4()[:8].upper()}",
                amount=round(product["price"] * random.uniform(0.8, 1.0), 2)  # Slight price variation
            )
            
            returns.append(return_record)
            session.add(return_record)
        
        session.commit()
        print(f"Generated {len(returns)} return records")
        return returns
    
    def generate_warranties(self, session: Session, num_warranties: int = 500) -> List[Warranty]:
        """Generate realistic warranty claim records."""
        warranties = []
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        
        for _ in range(num_warranties):
            # Generate random date in the last 90 days
            random_days = random.randint(0, 90)
            claim_date = end_date - timedelta(days=random_days)
            
            # Select random product with bias toward electronics and higher-priced items
            product = random.choice(self.products_data)
            if product["category"] not in ["Electronics", "Home & Garden"] and random.random() > 0.3:
                continue  # Lower warranty rate for clothing, etc.
            
            # Resolution time varies by complexity
            if product["category"] == "Electronics":
                resolution_time = random.randint(1, 14)  # 1-14 days for electronics
            else:
                resolution_time = random.randint(1, 7)   # 1-7 days for others
            
            # Some warranties might still be pending
            status = random.choice(self.statuses)
            if status in ["Pending", "In Progress"]:
                resolution_time = None
            
            warranty = Warranty(
                product_id=product["id"],
                claim_date=claim_date,
                issue_description=random.choice(self.warranty_issues),
                resolution_time_days=resolution_time,
                status=status,
                cost=round(random.uniform(10.0, product["price"] * 0.3), 2)  # Repair cost
            )
            
            warranties.append(warranty)
            session.add(warranty)
        
        session.commit()
        print(f"Generated {len(warranties)} warranty records")
        return warranties
    
    def generate_all_data(self, num_returns: int = 1000, num_warranties: int = 500):
        """Generate all seed data."""
        session = db_manager.get_session()
        
        try:
            print("Starting seed data generation...")
            
            # Create tables
            db_manager.create_tables()
            print("Database tables created")
            
            # Generate data in order (products first, then returns/warranties)
            products = self.generate_products(session)
            returns = self.generate_returns(session, num_returns)
            warranties = self.generate_warranties(session, num_warranties)
            
            print(f"Seed data generation completed successfully!")
            print(f"Summary: {len(products)} products, {len(returns)} returns, {len(warranties)} warranties")
            
        except Exception as e:
            print(f"Error generating seed data: {e}")
            session.rollback()
            raise
        finally:
            session.close()

if __name__ == "__main__":
    generator = SeedDataGenerator()
    generator.generate_all_data()