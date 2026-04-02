from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from app.core.database import Base

class PendingListing(Base):
    """
    Session cache to hold onto the AI generated parameters
    until the user approves them via WhatsApp.
    """
    __tablename__ = "pending_listings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Store AI & Pricing response as raw JSON to build SP-API payload later
    ai_data = Column(JSON, nullable=False)
    pricing_data = Column(JSON, nullable=False)
    
    status = Column(String, default="pending") # 'pending' or 'approved'
    sku = Column(String, unique=True, index=True)
