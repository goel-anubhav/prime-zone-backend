from app.core.config import Base
from sqlalchemy import String, UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid

class HeroSection(Base):
    
    """
    Table for Hero Section (Website Banner)
    """
    
    __tablename__ = "hero_sections"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=True)
    subtitle: Mapped[str] = mapped_column(String, nullable=True)
    image: Mapped[str] = mapped_column(String, nullable=False)
