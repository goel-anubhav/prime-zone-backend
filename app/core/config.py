""" 
Config File for Defining:

    - Logger
    - Env Loading Scheme 
    - Declarative Base for SQLAlchemy
"""

# Dependencies
from pydantic_settings import BaseSettings
from functools import lru_cache
from sqlalchemy.ext.declarative import declarative_base
import os
import logging
from logging.handlers import RotatingFileHandler

# Base Class for tables
Base = declarative_base()

# Define Logger & Logging Strat
def get_logger():
    
    """
    This function returns the logger for the application. It sets a handler that logs to a file, 
    and sets the logging level to INFO. If the logger already has a handler, it does not add another one.

    Returns:
        logger: The logger for the application
    """
    
    logger = logging.getLogger('uvicorn.info')
    logger.setLevel(logging.INFO)
    
    # Setting a handler for logging to a file
    handler = RotatingFileHandler("app.log", maxBytes=2000, backupCount=5)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger

# Configuration Variables
class Settings(BaseSettings):
    
    # Database Details
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # JWT Details
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    
    # Ibotix Admin Account
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL")
    ADMIN_PASS: str = os.getenv("ADMIN_PASS")
    
    # SMTP Details
    SMTP_URL: str = os.getenv("SMTP_URL")
    SMTP_PORT: int = os.getenv("SMTP_PORT")
    EMAIL: str = os.getenv("SMTP_EMAIL")
    PASSWORD: str = os.getenv("SMTP_PASSWORD")
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings():

    """
    Loads the configuration variables from the environment and returns them as a Settings object. The object is cached so
    that it is only loaded once. If an error occurs while loading the settings, it is logged and then re-raised.

    Returns:
        Settings: The configuration variables as a Settings object
    """
    logger = get_logger()
    try:
        settings = Settings()
        logger.info("Loading config settings from the environment...")
        return settings
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        raise e