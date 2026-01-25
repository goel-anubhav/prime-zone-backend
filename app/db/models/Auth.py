import uuid
from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from .UserBase import *
from datetime import timedelta
from app.db.enum import TokenStatus, AuthEvent
from app.core.config import Base
from datetime import datetime


"""
A script to define Authentication-Centric Database Tables Architecture:

Tables:
1. AuthToken: Centralised Table to Store all generated Auth Tokens
2. AuthLog: Table to Store all Authentication Logs
"""


class AuthToken(Base):

    __tablename__ = 'auth_tokens'

    # Details
    id: Mapped[str] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(), unique=True, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(), unique=True,)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    expires_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True, server_default=func.now() + timedelta(days=1))
    status: Mapped[TokenStatus] = mapped_column(Enum(TokenStatus), index=True, nullable=True, default=TokenStatus.ACTIVE)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped['User'] = relationship(back_populates='auth_tokens', lazy='noload')


class AuthLog(Base):
    
    __tablename__ = 'auth_logs'

    # Details
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    event: Mapped[AuthEvent] = mapped_column(Enum(AuthEvent), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    user_ip: Mapped[str] = mapped_column(String(), nullable=True)
    user_device: Mapped[str] = mapped_column(String(), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates='auth_logs', lazy='noload')