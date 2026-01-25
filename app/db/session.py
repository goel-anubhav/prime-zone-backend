import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.core.config import get_settings, get_logger
from typing import AsyncGenerator 
from app.core.config import Base
from app.db.models import *
from app.db.enum import UserStatus, UserType
from app.utility.misc import get_password_hash

# Loading Settings
settings = get_settings()
logger = get_logger()

# Create Async Engine
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True, 
                             pool_size=25, max_overflow=25, pool_pre_ping=True)


async def create_database_if_not_exists():
    
    """
    Asynchronous function to check if the database exists and create it if it doesn't.
    
    This function connects to the PostgreSQL server without specifying a database
    and checks for the existence of the target database. If it doesn't exist, it creates it.
    """
    
    # Parse the database URL to remove the 'asyncpg' driver and fallback to 'postgresql'
    database_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql").rsplit("/", 1)[0] + "/postgres"

    # Connect to PostgreSQL server (default 'postgres' database) without specifying the target database
    conn = await asyncpg.connect(database_url)
    
    # Check if the target database exists
    target_db_name = settings.DATABASE_URL.rsplit("/", 1)[1]
    result = await conn.fetchval(f"SELECT 1 FROM pg_database WHERE datname = '{target_db_name}'")
    
    if not result:
        # If the database does not exist, create it
        await conn.execute(f'CREATE DATABASE "{target_db_name}"')
        logger.info(f"Database '{target_db_name}' created successfully!")
    else:
        logger.info(f"Database '{target_db_name}' already exists.")
    
    await conn.close()


# Async db initiation
async def init_db():
    
    """
    Asynchronous function to initialize the database.
    
    This function is responsible for checking if the database exists, creating it if not,
    and then creating the tables based on the Base class.
    """
    
    logger.info("Checking if the database exists or needs to be created...")
    await create_database_if_not_exists()  # Ensure the database exists before proceeding
    
    async with engine.begin() as conn:
        logger.info("Creating tables in the database if they don't exist...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created successfully!")

# Async Session Generator
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    
    """
    Asynchronous generator to create a new session object.

    This asynchronous generator creates a new session object using the sessionmaker
    and the async engine. It uses an asynchronous context manager to ensure that
    the session is properly closed when it is no longer needed.

    Yields:
        AsyncSession: A new session object.
    """
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
            
async def drop_db():
    """
    Asynchronous function to drop all tables in the database.
    
    This is useful for testing or resetting the database state.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
async def Add_Ibotix_Admin(db: AsyncSession = get_session()):
    
    # Loading Creds
    ADMIN_EMAIL = settings.ADMIN_EMAIL
    ADMIN_PASS = settings.ADMIN_PASS
    
    async for session in db:
    
        # Checking if admin already exists
        #existing_admin = await session.execute(
        #    select(User).where(User.email == ADMIN_EMAIL),
        #)
        #existing_admin = existing_admin.scalars().first()
        
        #if not existing_admin:
            
        logger.info("Ibotix Admin Account does not exist..")
        
        # Create Admin User
        admin_user = User(
            user_type=UserType.ADMIN,
            name="Ibotix",
            email=ADMIN_EMAIL,
            password=get_password_hash(ADMIN_PASS),  # Securely hash the password
            user_status=UserStatus.ACTIVE,
        )
            
        session.add(admin_user)
        await session.commit()
        logger.info("Ibotix Admin Account added..")
        
        # Create admin profile
        admin_profile = AdminProfile(user_id=admin_user.id)
        session.add(admin_profile)
        await session.commit()
            
    else:
        logger.info("Ibotix Admin Account already exist..")
    
    
    