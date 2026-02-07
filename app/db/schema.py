from pydantic import BaseModel, EmailStr, ConfigDict
import datetime
from typing import List, Optional
from app.db.enum import UserStatus, UserType, AuthEvent
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
import uuid


# Base schema for Output
class BaseOutput(BaseModel):
    message: str
    detail: str

# Base schema for Reading a User
class UserRead(BaseModel):
    name: str
    email: EmailStr
    first_login: bool
    user_status: UserStatus = UserStatus.ACTIVE
    user_type: UserType

    class Config:
        from_attributes = True

# Response for Login  
class LoginResponse(BaseModel):

    user_details: UserRead
    message: str
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    
    class Config:
        from_attributes = True
        
# Response for Admin Registration  
class AdminRegistration(BaseModel):

    name: str
    email: EmailStr
    password: str
    user_status: UserStatus = UserStatus.PENDING
    
    class Config:
        from_attributes = True
        
        
# Response for Broker Registration  
class BrokerRegistration(BaseModel):

    name: str
    email: EmailStr
    password: str
    user_status: UserStatus = UserStatus.PENDING
    
    class Config:
        from_attributes = True
        
# Response for BrokerAlias Registration  
class BrokerAliasRegistration(BaseModel):

    name: str
    email: EmailStr
    password: str
    user_status: UserStatus = UserStatus.PENDING
    
    class Config:
        from_attributes = True
        
# Response for Agent Registration  
class AgentRegistration(BaseModel):

    name: str
    email: EmailStr
    password: str
    user_status: UserStatus = UserStatus.PENDING
    
    class Config:
        from_attributes = True

# Request Schema for Refresh Token
class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Response Schema for Refresh Token
class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

# Service Schemas
class ServiceBase(BaseModel):
    title: str
    category: str
    
    heading1: Optional[str] = None
    heading2: Optional[str] = None
    
    detail1: Optional[str] = None
    detail2: Optional[str] = None
    
    image1: Optional[str] = None
    image2: Optional[str] = None
    
    class Config:
        from_attributes = True

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(ServiceBase):
    pass

class ServiceResponse(ServiceBase):
    id: uuid.UUID

# Portfolio Schemas
class PortfolioBase(BaseModel):
    title: str
    category: str
    description: Optional[str] = None
    image: Optional[str] = None
    
    class Config:
        from_attributes = True

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioUpdate(PortfolioBase):
    pass

class PortfolioResponse(PortfolioBase):
    id: uuid.UUID

# Hero Section Schemas
class HeroBase(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    image: str
    
    class Config:
        from_attributes = True

class HeroCreate(HeroBase):
    pass

class HeroUpdate(HeroBase):
    pass

class HeroResponse(HeroBase):
    id: uuid.UUID