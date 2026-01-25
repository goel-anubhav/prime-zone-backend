import uuid
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Enum, UUID, Table, Column, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.core.config import Base
from .Auth import AuthLog, AuthToken
from app.db.enum import UserStatus, UserType
from datetime import datetime
from typing import List


"""
A script to define User Centric Database Tables Architecture:

Tables:
0.5 Association table (Broker & Agents)
1. User: Centralized User Table for all UserTypes
2. AdminProfile: User Profiles with Admin Privileges
3. BrokerProfile: User Profiles with Broker Privileges
4. BrokerAliasProfile: User Profiles who are Broker Employees
5. AgentProfile: User Profiles with Agent Privileges
"""

# Association table for Many-to-Many relationship between Brokers and Agents
broker_agent_association = Table(
    'broker_agent_association',
    Base.metadata,
    Column("broker_id", ForeignKey("broker_profiles.user_id"), primary_key=True),
    Column("agent_id", ForeignKey("agent_profiles.user_id"), primary_key=True)
)


class User(Base):
    
    """
    Table for Users | Base Class for all Users: Admin, Broker, Broker_Alias, Agent
    """
    
    __tablename__ = "users"
    
    #Details
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    user_type: Mapped[UserType] = mapped_column(Enum(UserType), nullable=False, index=True)  
    name: Mapped[str] = mapped_column(String, default=None, nullable=False)  
    email: Mapped[str] = mapped_column(String, default=None, unique=True, nullable=False, index=True)  
    password: Mapped[str] = mapped_column(String, nullable=False, index=True)  
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)  
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)  
    
    #Flags
    first_login: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  
    pass_reset_token: Mapped[str] = mapped_column(String, nullable=True)  
    user_status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), nullable=False, default=UserStatus.PENDING, index=True)  
    
    # Relationships to profile tables
    admin_profile = relationship("AdminProfile", back_populates="user", uselist=False)  
    broker_profile = relationship("BrokerProfile", back_populates="user", uselist=False) 
    broker_alias_profile = relationship("BrokerAliasProfile", back_populates="user", uselist=False)  
    agent_profile = relationship("AgentProfile", back_populates="user", uselist=False)
    auth_tokens: Mapped['AuthToken'] = relationship(back_populates='user', lazy='noload')
    auth_logs: Mapped['AuthLog'] = relationship(back_populates='user', lazy='noload')  


class AdminProfile(Base):
    
    """
    Table for User Profiles with Admin Privileges
    """
    
    __tablename__ = "admin_profiles"
    
    # Details
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)  
    
    # Relationship
    user = relationship("User", back_populates="admin_profile")  


class BrokerProfile(Base):
    
    """
    Table for User Profiles with Broker Privileges
    """
    
    __tablename__ = "broker_profiles"

    # Details
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True) 
    broker_key: Mapped[str] = mapped_column(String, nullable=False) 

    # Relationships
    user = relationship("User", back_populates="broker_profile") 
    aliases = relationship("BrokerAliasProfile", back_populates="broker", cascade="all, delete-orphan")  
    agents = relationship("AgentProfile", secondary=broker_agent_association, 
                          back_populates="brokers")  
    

class BrokerAliasProfile(Base):
    
    """
    Table for User Profiles with Broker Alias Privileges
    """
    
    __tablename__ = "broker_alias_profiles"

    # Details
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)  
    broker_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("broker_profiles.user_id"), nullable=False)  

    # Relationships
    user = relationship("User", back_populates="broker_alias_profile")  
    broker = relationship("BrokerProfile", back_populates="aliases")  
    agents = relationship("AgentProfile", back_populates="broker_alias")  


class AgentProfile(Base):

    """
    Table for User Profiles with Agent Privileges
    """
    __tablename__ = "agent_profiles"

    # Details
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)  
    broker_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("broker_profiles.user_id"), nullable=False)  
    broker_alias_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("broker_alias_profiles.user_id"), nullable=True)  
    prospect_id: Mapped[str] = mapped_column(String, nullable=True)  
    
    # Relationships
    user = relationship("User", back_populates="agent_profile")  
    brokers = relationship("BrokerProfile", secondary=broker_agent_association, 
                           back_populates="agents")  
    broker_alias = relationship("BrokerAliasProfile", back_populates="agents") 
