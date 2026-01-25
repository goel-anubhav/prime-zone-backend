from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from app.db.schema import (LoginResponse, BaseOutput, AdminRegistration, BrokerRegistration, 
                           BrokerAliasRegistration, AgentRegistration)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from random import randint
from app.db.session import get_session
from app.db.models import *
from app.db.enum import TokenStatus, AuthEvent, UserStatus, UserType
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_200_OK
from datetime import timedelta
from sqlalchemy import select, and_, func
from typing import Annotated
from app.utility.misc import (decode_token, verify_password, create_access_token, 
                              create_refresh_token, get_password_hash)
from app.core.config import get_settings,get_logger
from app.utility.CustomException import CustomHttpException

# Load Env and Logger
settings=get_settings()
logger = get_logger()


# init Router
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_active_user(token:str = Depends(oauth2_scheme),db: AsyncSession = Depends(get_session))-> User:
    
    """
    Retrieves the current user based on the provided token and database session.

    Args:
        token (str): The access token to authenticate the user. Defaults to Depends(oauth2_scheme).
        db (AsyncSession): The database session to query the user data. Defaults to Depends(get_session).

    Returns:
        User
    """
    
    credentials_exception = CustomHttpException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        message="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:

        payload = decode_token(token, token_type="access")
        
        username: str = payload.get("sub")
        if not username:
            logger.error("Error in get_active_user: Username null in token payload")
            raise credentials_exception
            
        else:
            stmt = select(User).where(User.email == username, User.user_status == UserStatus.ACTIVE)
            user = await db.execute(stmt)
            user = user.scalars().first()
            auth_token = await db.execute(select(AuthToken).where(AuthToken.token == token).where(AuthToken.status == TokenStatus.ACTIVE and AuthToken.expires_at > datetime.now()))
            auth_token = auth_token.scalars().first()
            
            if not auth_token:
                logger.error("Error in get_active_user: Token record not found or inactive/expired in DB")
                raise credentials_exception
            

            if user is None:
                logger.error(f"Error in get_active_user: User not found for email {username}")
                raise credentials_exception
            return user
        
    except Exception as e:
        if isinstance(e, CustomHttpException):
            raise e
        
        else:
            logger.error(f"Error in get_active_user: {str(e)}")
            raise credentials_exception

# Endpoint for Login
@router.post("/login", responses={200: {"model": LoginResponse}})
async def login(
    data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    db: AsyncSession = Depends(get_session),
):

    """
    Handles the login of an Admin.

    Args:
        data (OAuth2PasswordRequestForm): The login data.
        request (Request): The incoming request.
        db (AsyncSession): The database session.

    Returns:
        LoginResponse: A response message indicating the status of the login.

    Raises:
        CustomHttpException: If the user is unauthorized or if an internal server error occurs.
    """
    
    try:
        username = data.username
        password = data.password
        user = await db.execute(
            select(User).where(User.email == username).where(User.user_status == UserStatus.ACTIVE)
        )
        user = user.scalars().first()

        if not user or not verify_password(password, user.password):
            raise CustomHttpException(
                status_code=HTTP_401_UNAUTHORIZED, 
                detail="Invalid Email or Password", 
                message="Login Unsuccessful"
            )

        # TODO: Email Verfication POC
        #if not user.email_verified:
        #    raise CustomHttpException(
        #        status_code=HTTP_401_UNAUTHORIZED, 
        #        detail="Email not verified", 
        #        message="Login Unsuccessful"
        #    )

        token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})

        auth_token = AuthToken(
            user_id=user.id, 
            token=token, 
            refresh_token=refresh_token,
            status=TokenStatus.ACTIVE,
            expires_at=func.now() + timedelta(days=30)
        )
        db.add(auth_token)
        await db.commit()
        
        if auth_token:
            
            auth_log = AuthLog(user_id=user.id, 
                               event=AuthEvent.LOGIN, 
                               timestamp=func.now(),
                               user_ip=request.client.host,
                               user_device=request.headers.get('User-Agent')
                               )
            db.add(auth_log)
            await db.commit()

        response = JSONResponse(
            content={
                "user_details": {
                    "name": user.name,
                    "email": user.email,
                    "first_login": user.first_login,
                    "user_status": str(user.user_status),
                    "user_type": str(user.user_type)
                },
                "message": "Login Successful", 
                "access_token": token, 
                "refresh_token": refresh_token,
                "token_type": "bearer"
            },
            status_code=HTTP_200_OK,
        )
        response.set_cookie(key="Access_token", value=token, httponly=True, expires=timedelta(minutes=15))
        response.set_cookie(key="Refresh_token", value=refresh_token, httponly=True, expires=timedelta(days=30))
        
        return response

    except Exception as e:
        logger.error(str(e))
        raise CustomHttpException(status_code=500, detail="Internal Server Error", message="Error logging user")


# Endpoint for Admin Registration
@router.post("/register_admin", responses = {200: {"model": BaseOutput}})
async def register_admin(
    payload: AdminRegistration,
    request: Request,
    user: User = Depends(get_active_user),
    db: AsyncSession = Depends(get_session),
):
    
    """
    Handles the registration of a new Admin.

    Args:
        payload (UserCreate): Admin registration data.
        request (Request): The incoming request.
        user (User): The user object obtained from the token.
        db (AsyncSession): The database session.

    Returns:
        BaseOutput: A response message indicating the status of the registration.

    Raises:
        CustomHttpException: If the user already exists or if an internal server error occurs.
    """
    
    # Check User
    if not user:
        raise CustomHttpException(status_code=HTTP_404_NOT_FOUND,
                                  message="User Not Found",
                                  detail="Invalid Session Access Token"
                                  )
    
    
    # Check for active user is Ibotix or not
    if user.email != settings.ADMIN_EMAIL:
        raise CustomHttpException(status_code=HTTP_401_UNAUTHORIZED,
                                  message="User Not Authorized",
                                  detail="Only Ibotix-Admin can create Admin Accounts")
    
    try:
        
        # Create Admin User
        admin_user = User(
            user_type=UserType.ADMIN,
            name=payload.name,
            email=payload.email,
            password=get_password_hash(payload.password),  # Securely hash the password
            user_status=UserStatus.ACTIVE,
        )
            
        db.add(admin_user)
        await db.commit()

        # Create admin profile
        admin_profile = AdminProfile(user_id=admin_user.id)
        db.add(admin_profile)
        await db.commit()
        
        # Auth Log
        if admin_user:
                
                auth_log = AuthLog(user_id=admin_user.id, 
                                event=AuthEvent.REGISTER, 
                                timestamp=func.now(),
                                user_ip=request.client.host,
                                user_device=request.headers.get('User-Agent')
                                )
                db.add(auth_log)
                await db.commit()
        
        response = JSONResponse(
            content={
                "message" : "New Admin Added",
                "detail" :  f"New Admin {admin_user.name} Added Successfully"
            },
            status_code=HTTP_200_OK
        )
        
        return response
        
    except Exception as e:
        logger.error(str(e))
        raise CustomHttpException(status_code=500, detail="Internal Server Error", message="Error logging user")


# # Endpoint for Broker Registration
# @router.post("/register_broker", responses = {200: {"model": BaseOutput}})
# async def register_broker(
#     payload: BrokerRegistration,
#     request: Request,
#     user: User = Depends(get_active_user),
#     db: AsyncSession = Depends(get_session),
# ):
    
#     """
#     Handles the registration of a new Broker.

#     Args:
#         payload (UserCreate): Broker registration data.
#         request (Request): The incoming request.
#         user (User): The user object obtained from the token.
#         db (AsyncSession): The database session.

#     Returns:
#         BaseOutput: A response message indicating the status of the registration.

#     Raises:
#         CustomHttpException: If the user already exists or if an internal server error occurs.
#     """
    
#     # Check User
#     if not user:
#         raise CustomHttpException(status_code=HTTP_404_NOT_FOUND,
#                                   message="User Not Found",
#                                   detail="Invalid Session Access Token"
#                                   )
    
    
#     # Check for active user is Admin or not
#     if user.user_type != UserType.ADMIN:
#         raise CustomHttpException(status_code=HTTP_401_UNAUTHORIZED,
#                                   message="User Not Authorized",
#                                   detail="Only Admins can create Broker Accounts")
    
#     try:
        
#         # Create Broker User
#         broker_user = User(
#             user_type=UserType.BROKER,
#             name=payload.name,
#             email=payload.email,
#             password=get_password_hash(payload.password),  # Securely hash the password
#             user_status=UserStatus.ACTIVE,
#         )
            
#         db.add(broker_user)
#         await db.commit()

#         # Create admin profile
#         broker_profile = BrokerProfile(user_id=broker_user.id,
#                                        broker_key=str(broker_user.name[:3]).upper() + str(randint(420,999)),
#                         )
#         db.add(broker_profile)
#         await db.commit()
        
#         # Auth Log
#         if broker_user:
                
#                 auth_log = AuthLog(user_id=broker_user.id, 
#                                 event=AuthEvent.REGISTER, 
#                                 timestamp=func.now(),
#                                 user_ip=request.client.host,
#                                 user_device=request.headers.get('User-Agent')
#                                 )
#                 db.add(auth_log)
#                 await db.commit()
        
#         response = JSONResponse(
#             content={
#                 "message" : "New Broker Added",
#                 "detail" :  f"New Broker {broker_user.name} Added Successfully"
#             },
#             status_code=HTTP_200_OK
#         )
        
#         return response
        
#     except Exception as e:
#         logger.error(str(e))
#         raise CustomHttpException(status_code=500, detail="Internal Server Error", message="Error logging user")
    
    
# # Endpoint for BrokerAlias Registration
# @router.post("/register_broker_alias", responses = {200: {"model": BaseOutput}})
# async def register_broker_alias(
#     payload: BrokerAliasRegistration,
#     request: Request,
#     user: User = Depends(get_active_user),
#     db: AsyncSession = Depends(get_session),
# ):
    
#     """
#     Handles the registration of a new Broker Alias.

#     Args:
#         payload (UserCreate): Broker registration data.
#         request (Request): The incoming request.
#         user (User): The user object obtained from the token.
#         db (AsyncSession): The database session.

#     Returns:
#         BaseOutput: A response message indicating the status of the registration.

#     Raises:
#         CustomHttpException: If the user already exists or if an internal server error occurs.
#     """
    
#     # Check User
#     if not user:
#         raise CustomHttpException(status_code=HTTP_404_NOT_FOUND,
#                                   message="User Not Found",
#                                   detail="Invalid Session Access Token"
#                                   )
    
    
#     # Check for active user is broker or not
#     if user.user_type != UserType.BROKER:
#         raise CustomHttpException(status_code=HTTP_401_UNAUTHORIZED,
#                                   message="User Not Authorized",
#                                   detail="Only Broker can create Broker Alias Accounts")
    
#     try:
        
#         # Create Broker Alias User
#         broker_alias_user = User(
#             user_type=UserType.BROKER_ALIAS,
#             name=payload.name,
#             email=payload.email,
#             password=get_password_hash(payload.password),  # Securely hash the password
#             user_status=UserStatus.ACTIVE,
#         )
            
#         db.add(broker_alias_user)
#         await db.commit()

#         # Create admin profile
#         broker_profile = BrokerAliasProfile(user_id=broker_alias_user.id,
#                                             broker_id=user.id)
#         db.add(broker_profile)
#         await db.commit()
        
#         # Auth Log
#         if broker_alias_user:
                
#                 auth_log = AuthLog(user_id=broker_alias_user.id, 
#                                 event=AuthEvent.REGISTER, 
#                                 timestamp=func.now(),
#                                 user_ip=request.client.host,
#                                 user_device=request.headers.get('User-Agent')
#                                 )
#                 db.add(auth_log)
#                 await db.commit()
        
#         response = JSONResponse(
#             content={
#                 "message" : "New Broker Alias Added",
#                 "detail" :  f"New Broker Alias {broker_alias_user.name} Added Successfully"
#             },
#             status_code=HTTP_200_OK
#         )
        
#         return response
        
#     except Exception as e:
#         logger.error(str(e))
#         raise CustomHttpException(status_code=500, detail="Internal Server Error", message="Error logging user")
    
# # Endpoint for Agent Registration
# @router.post("/register_agent", responses = {200: {"model": BaseOutput}})
# async def register_agent(
#     payload: AgentRegistration,
#     request: Request,
#     user: User = Depends(get_active_user),
#     db: AsyncSession = Depends(get_session),
# ):
    
#     """
#     Handles the registration of a new Agent.

#     Args:
#         payload (AgentRegistration): Agent registration data.
#         request (Request): The incoming request.
#         user (User): The user object obtained from the token.
#         db (AsyncSession): The database session.

#     Returns:
#         BaseOutput: A response message indicating the status of the registration.

#     Raises:
#         CustomHttpException: If the user already exists or if an internal server error occurs.
#     """
    
#     # Check User
#     if not user:
#         raise CustomHttpException(status_code=HTTP_404_NOT_FOUND,
#                                   message="User Not Found",
#                                   detail="Invalid Session Access Token"
#                                   )
    
    
#     # Check for active user is broker or broker alias
#     if user.user_type not in [UserType.BROKER, UserType.BROKER_ALIAS]:
#         raise CustomHttpException(status_code=HTTP_401_UNAUTHORIZED,
#                                   message="User Not Authorized",
#                                   detail="Only Broker/Alias can create Agent Accounts")
    
#     try:
        
#         # Create Broker Alias User
#         agent_user = User(
#             user_type=UserType.AGENT,
#             name=payload.name,
#             email=payload.email,
#             password=get_password_hash(payload.password),  # Securely hash the password
#             user_status=UserStatus.ACTIVE,
#         )
            
#         db.add(agent_user)
#         await db.commit()

#         # Create admin profile
#         if user.user_type == UserType.BROKER:
            
#             agent_profile = AgentProfile(user_id=agent_user.id,
#                                                 broker_id=user.id)
        
#         elif user.user_type == UserType.BROKER_ALIAS:
            
#             # Extracted Alias Profile
#             broker_alias_profile = await db.execute(
#                 select(BrokerAliasProfile).where(BrokerAliasProfile.user_id == user.id)
#             )
#             broker_alias_profile = broker_alias_profile.scalars().first()
            
#             if broker_alias_profile is None:
             
#                 raise CustomHttpException(status_code=HTTP_404_NOT_FOUND,
#                                   message="No Broker Alias Found",
#                                   detail="Broker Alias Profile is not found associated witht the Broker Alias Account")
 
#             agent_profile = AgentProfile(user_id=agent_user.id,
#                                          broker_id=broker_alias_profile.broker_id)
            
#         else:

#             raise CustomHttpException(status_code=HTTP_401_UNAUTHORIZED,
#                                   message="User Not Authorized",
#                                   detail="Only Broker/Alias can create Agent Accounts")
#         db.add(agent_profile)
#         await db.commit()

#         # Auth Log
#         if agent_user:
 
#             auth_log = AuthLog(user_id=agent_user.id, 
#                             event=AuthEvent.REGISTER, 
#                             timestamp=func.now(),
#                             user_ip=request.client.host,
#                             user_device=request.headers.get('User-Agent'))
            
#             db.add(auth_log)
#             await db.commit()

#         response = JSONResponse(
#             content={
#                 "message" : "New Agent Added",
#                 "detail" :  f"New Agent {agent_user.name} Added Successfully"
#             },
#             status_code=HTTP_200_OK
#         )
        
#         return response
        
#     except Exception as e:
#         logger.error(str(e))
#         raise CustomHttpException(status_code=500, detail="Internal Server Error", message="Error logging user")