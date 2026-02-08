from app.core.config import Base
from sqlalchemy import String, Integer, Column, UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid

class Service(Base):
    
    """
    Table for Services
    """
    
    __tablename__ = "services"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=True)
    
    heading1: Mapped[str] = mapped_column(String, nullable=True)
    heading2: Mapped[str] = mapped_column(String, nullable=True)
    
    detail1: Mapped[str] = mapped_column(String, nullable=True)
    detail2: Mapped[str] = mapped_column(String, nullable=True)
    
    image1: Mapped[str] = mapped_column(String, nullable=True)
    image2: Mapped[str] = mapped_column(String, nullable=True)
