from pydantic import BaseModel, EmailStr, ConfigDict
import datetime
from typing import List, Optional
from app.db.enum import UserStatus, UserType, AuthEvent
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED


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