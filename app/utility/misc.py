from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import get_settings, get_logger
from fastapi.security import OAuth2PasswordBearer

# OAuth2 Scheme Init
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Loading Settings
settings = get_settings()
logger = get_logger()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Create access token
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    
    """
    Create an access token

    Args:
        data (dict): A dictionary with the payload of the token
        expires_delta (timedelta, optional): The time in which the token will expire. Defaults to None.

    Returns:
        str: The encoded JWT token
    """
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Create refresh token
def create_refresh_token(data: dict) -> str:
    
    """
    Create a refresh token. This is just a wrapper around create_access_token
    with a longer expiration time.

    Args:
        data (dict): A dictionary with the payload of the token

    Returns:
        str: The encoded JWT token
    """
    
    return create_access_token(data, timedelta(days=30))

# Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    
    """
    Verify a plaintext password against its hashed version.

    Args:
        plain_password (str): The plaintext password to verify.
        hashed_password (str): The hashed version of the password.

    Returns:
        bool: Whether the plaintext password matches the hashed password.
    """
    
    return pwd_context.verify(plain_password, hashed_password)

# Hash password
def get_password_hash(password: str) -> str:
    
    """
    Hash a plaintext password using the configured password hash algorithm.

    Args:
        password (str): The plaintext password to hash.

    Returns:
        str: The hashed version of the password.
    """
    
    return pwd_context.hash(password)

# Decode JWT token
def decode_token(token: str, token_type="access"):
    
    """
    Decode a JWT token.

    Args:
        token (str): The JWT token to decode.
        token_type (str, optional): The type of the token. Defaults to "access".

    Returns:
        dict: The decoded payload of the token.

    Raises:
        ValueError: If the token is invalid.
    """
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")
    

