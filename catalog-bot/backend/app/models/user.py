from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    whatsapp_phone = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    credentials = relationship("EcomCredentials", back_populates="owner", cascade="all, delete-orphan")

class EcomCredentials(Base):
    __tablename__ = "ecom_credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String, nullable=False) # 'amazon' or 'flipkart'
    
    # Encrypted fields
    encrypted_access_token = Column(String, nullable=False)
    encrypted_refresh_token = Column(String, nullable=True)
    seller_id = Column(String, nullable=True) 
    
    owner = relationship("User", back_populates="credentials")
