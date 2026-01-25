from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid
import shutil
import os

from app.db.session import get_session
from app.db.models import HeroSection, User
from app.db.schema import HeroResponse, BaseOutput
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

@router.get("/", response_model=List[HeroResponse])
async def get_hero_sections(
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(HeroSection))
    hero_sections = result.scalars().all()
    return hero_sections

@router.post("/", response_model=HeroResponse)
async def create_hero_section(
    image: UploadFile = File(...),
    title: Optional[str] = Form(None),
    subtitle: Optional[str] = Form(None),
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

    # Create Hero
    new_hero = HeroSection(
        title=title,
        subtitle=subtitle,
        image=image_url
    )
    db.add(new_hero)
    await db.commit()
    await db.refresh(new_hero)
    return new_hero

@router.put("/{id}", response_model=HeroResponse)
async def update_hero_section(
    id: uuid.UUID,
    title: Optional[str] = Form(None),
    subtitle: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(check_admin)
):
    result = await db.execute(select(HeroSection).where(HeroSection.id == id))
    hero = result.scalars().first()
    if not hero:
        raise HTTPException(status_code=404, detail="Hero Section not found")
    
    # Update Fields
    if title is not None:
        hero.title = title
    if subtitle is not None:
        hero.subtitle = subtitle
    
    # Handle Image Update
    if image:
        try:
            file_extension = image.filename.split(".")[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(STATIC_DIR, file_name)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            hero.image = f"/static/{file_name}"
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
    
    await db.commit()
    await db.refresh(hero)
    return hero
