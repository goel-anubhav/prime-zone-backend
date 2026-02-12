from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid
import shutil
import os

from app.db.session import get_session
from app.db.models import Portfolio, User
from app.db.schema import PortfolioResponse, BaseOutput
from app.routes.auth import get_active_user
from app.db.enum import UserType

router = APIRouter()

STATIC_DIR = "static"

async def check_admin(user: User = Depends(get_active_user)):
    if user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admins can perform this action"
        )
    return user

@router.get("", response_model=List[PortfolioResponse])
async def get_all_portfolios(
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(Portfolio))
    portfolios = result.scalars().all()
    return portfolios

@router.get("/{id}", response_model=PortfolioResponse)
async def get_portfolio(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(check_admin)
):
    result = await db.execute(select(Portfolio).where(Portfolio.id == id))
    portfolio = result.scalars().first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio Item not found")
    return portfolio

@router.post("", response_model=PortfolioResponse)
async def create_portfolio(
    title: str = Form(...),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(check_admin)
):
    # Save Image
    try:
        file_extension = image.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(STATIC_DIR, file_name)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        image_url = f"/static/{file_name}"
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

    # Create Portfolio
    new_portfolio = Portfolio(
        title=title,
        category=category,
        description=description,
        image=image_url
    )
    db.add(new_portfolio)
    await db.commit()
    await db.refresh(new_portfolio)
    return new_portfolio

@router.put("/{id}", response_model=PortfolioResponse)
async def update_portfolio(
    id: uuid.UUID,
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(check_admin)
):
    result = await db.execute(select(Portfolio).where(Portfolio.id == id))
    portfolio = result.scalars().first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio Item not found")
    
    # Update Fields
    if title:
        portfolio.title = title
    if category:
        portfolio.category = category
    if description:
        portfolio.description = description
    
    # Handle Image Update
    if image:
        try:
            # Delete old image if exists? (Optional improvement)
            
            file_extension = image.filename.split(".")[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(STATIC_DIR, file_name)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            portfolio.image = f"/static/{file_name}"
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
    
    await db.commit()
    await db.refresh(portfolio)
    return portfolio

@router.delete("/{id}", response_model=BaseOutput)
async def delete_portfolio(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(check_admin)
):
    result = await db.execute(select(Portfolio).where(Portfolio.id == id))
    portfolio = result.scalars().first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio Item not found")
    
    # Optionally delete the image file here
    
    await db.delete(portfolio)
    await db.commit()
    return BaseOutput(message="Portfolio Item deleted successfully", detail=f"Portfolio Item with id {id} has been deleted")
