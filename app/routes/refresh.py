from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.db.schema import RefreshTokenRequest, RefreshTokenResponse
from app.utility.misc import decode_token, create_access_token, create_refresh_token
from app.db.models import AuthToken
from app.db.enum import TokenStatus
from sqlalchemy import select, func
from datetime import datetime
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from app.utility.CustomException import CustomHttpException
from app.core.config import get_settings, get_logger
from datetime import timedelta

settings = get_settings()
logger = get_logger()
router = APIRouter()

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_session)
):
    """
    Refresh access token using a valid refresh token.
    Invalidates the old refresh token and issues a new pair.
    """
    
    credentials_exception = CustomHttpException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        message="Invalid or expired refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the refresh token
        payload = decode_token(request.refresh_token, token_type="refresh")
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception

        # Check if the refresh token exists in the database and is active
        stmt = select(AuthToken).where(
            AuthToken.refresh_token == request.refresh_token,
            AuthToken.status == TokenStatus.ACTIVE
        )
        result = await db.execute(stmt)
        auth_token_record = result.scalars().first()

        if not auth_token_record:
            raise credentials_exception

        # Check if the token is expired (DB check)
        if auth_token_record.expires_at < datetime.now():
            auth_token_record.status = TokenStatus.INACTIVE
            await db.commit()
            raise credentials_exception

        # Invalidate the old refresh token
        auth_token_record.status = TokenStatus.INACTIVE
        db.add(auth_token_record)
        
        # Generate new tokens
        new_access_token = create_access_token(data={"sub": email})
        new_refresh_token = create_refresh_token(data={"sub": email})
        
        # Create new AuthToken record
        new_auth_token_record = AuthToken(
            user_id=auth_token_record.user_id,
            token=new_access_token,
            refresh_token=new_refresh_token,
            status=TokenStatus.ACTIVE,
            expires_at=datetime.now() + timedelta(days=30)
        )
        
        db.add(new_auth_token_record)
        await db.commit()
        await db.refresh(new_auth_token_record)

        return RefreshTokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )

    except Exception as e:
        if isinstance(e, CustomHttpException):
            raise e
        logger.error(f"Refresh token error: {e}")
        raise credentials_exception
