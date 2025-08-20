"""
Database models for retail returns and warranty data.
"""

from sqlalchemy import Column, Integer, String, Date, Text, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from multi_agent.config.database import Base
from datetime import date
from typing import Optional

class Product(Base):
    """Product catalog table."""
    __tablename__ = "products"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    brand = Column(String(100), nullable=False)
    
    # Relationships
    returns = relationship("Return", back_populates="product")
    warranties = relationship("Warranty", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id='{self.id}', name='{self.name}', category='{self.category}')>"

class Return(Base):
    """Returns data table."""
    __tablename__ = "returns"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50), nullable=False)
    product_id = Column(String(50), ForeignKey('products.id'), nullable=False)
    return_date = Column(Date, nullable=False)
    reason = Column(String(255), nullable=False)
    resolution_status = Column(String(50), nullable=False)
    store_location = Column(String(100), nullable=False)
    customer_id = Column(String(50), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="returns")
    
    def __repr__(self):
        return f"<Return(id={self.id}, product_id='{self.product_id}', reason='{self.reason}')>"

class Warranty(Base):
    """Warranty claims table."""
    __tablename__ = "warranties"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), ForeignKey('products.id'), nullable=False)
    claim_date = Column(Date, nullable=False)
    issue_description = Column(Text, nullable=False)
    resolution_time_days = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False)
    cost = Column(DECIMAL(10, 2), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="warranties")
    
    def __repr__(self):
        return f"<Warranty(id={self.id}, product_id='{self.product_id}', status='{self.status}')>"

# Data transfer objects for API responses
class ProductDTO:
    """Product data transfer object."""
    def __init__(self, product: Product):
        self.id = product.id
        self.name = product.name
        self.category = product.category
        self.price = float(product.price)
        self.brand = product.brand

class ReturnDTO:
    """Return data transfer object."""
    def __init__(self, return_record: Return):
        self.id = return_record.id
        self.order_id = return_record.order_id
        self.product_id = return_record.product_id
        self.return_date = return_record.return_date.isoformat()
        self.reason = return_record.reason
        self.resolution_status = return_record.resolution_status
        self.store_location = return_record.store_location
        self.customer_id = return_record.customer_id
        self.amount = float(return_record.amount)

class WarrantyDTO:
    """Warranty data transfer object."""
    def __init__(self, warranty: Warranty):
        self.id = warranty.id
        self.product_id = warranty.product_id
        self.claim_date = warranty.claim_date.isoformat()
        self.issue_description = warranty.issue_description
        self.resolution_time_days = warranty.resolution_time_days
        self.status = warranty.status
        self.cost = float(warranty.cost)