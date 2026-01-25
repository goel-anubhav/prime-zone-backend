import uuid
from sqlalchemy import String, DateTime, UUID
from sqlalchemy import func
from sqlalchemy.orm import mapped_column, Mapped
from app.core.config import Base
from datetime import datetime

"""
A script to define Database Tables Architecture | Data Storage for Prospects:

Tables:
1. Prospect: Centralised Table for all Prospective Customers
"""

class Prospect(Base):
    
    """
    Table for Prospect (Customers from Agents)
    """
    
    __tablename__ = "prospects"
    
    #Details
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, default=None, nullable=False)
    email: Mapped[str] = mapped_column(String, default=None, unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)