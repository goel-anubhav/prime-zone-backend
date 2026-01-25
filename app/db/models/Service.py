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
    image: Mapped[str] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=False)
    details: Mapped[str] = mapped_column(String, nullable=True)
