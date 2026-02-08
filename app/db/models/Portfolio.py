from app.core.config import Base
from sqlalchemy import String, Column, UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid

class Portfolio(Base):
    
    """
    Table for Portfolio Items
    """
    
    __tablename__ = "portfolios"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    image: Mapped[str] = mapped_column(String, nullable=True)
